#!/usr/bin/env python3
"""
Hide and Seek - Desktop GUI Video Trimmer & Audio Extractor
"""
import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    USE_CTK = True
except ImportError:
    USE_CTK = False

from process_video import parse_timestamp, process_video

try:
    from moviepy import VideoFileClip
except ImportError:
    try:
        from moviepy.editor import VideoFileClip
    except ImportError:
        VideoFileClip = None


def format_seconds(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format string."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:05.2f}"
    return f"{m:02d}:{s:05.2f}"


class MediaProcessorApp(ctk.CTk if USE_CTK else tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Hide and Seek - Video Trimmer & Audio Extractor")
        self.geometry("780x640")
        self.minsize(700, 580)

        # Set window icon if available
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        self.video_duration = 0.0
        self.is_processing = False

        self._build_ui()

    def _build_ui(self):
        # Header / Title
        header_frame = ctk.CTkFrame(self, corner_radius=10) if USE_CTK else tk.Frame(self)
        header_frame.pack(fill="x", padx=16, pady=(16, 8))

        title_lbl = (
            ctk.CTkLabel(
                header_frame,
                text="🎬 Hide and Seek — Media Studio",
                font=ctk.CTkFont(size=20, weight="bold"),
            )
            if USE_CTK
            else tk.Label(header_frame, text="Hide and Seek — Media Studio", font=("Segoe UI", 16, "bold"))
        )
        title_lbl.pack(pady=8, padx=12, anchor="w")

        # 1. Source File Frame
        file_frame = ctk.CTkFrame(self, corner_radius=10) if USE_CTK else tk.LabelFrame(self, text="Source Video")
        file_frame.pack(fill="x", padx=16, pady=8)

        src_lbl = ctk.CTkLabel(file_frame, text="Source Video File:", font=ctk.CTkFont(weight="bold")) if USE_CTK else tk.Label(file_frame, text="Source Video File:")
        src_lbl.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        self.entry_input = ctk.CTkEntry(file_frame, placeholder_text="Select a video file (MP4, MKV, MOV, AVI)...", width=500) if USE_CTK else tk.Entry(file_frame, width=60)
        self.entry_input.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")

        btn_browse_src = ctk.CTkButton(file_frame, text="Browse...", width=100, command=self._browse_input_file) if USE_CTK else tk.Button(file_frame, text="Browse...", command=self._browse_input_file)
        btn_browse_src.grid(row=1, column=1, padx=(0, 12), pady=(0, 10))

        file_frame.grid_columnconfigure(0, weight=1)

        self.lbl_file_info = ctk.CTkLabel(file_frame, text="No video loaded.", text_color="gray70") if USE_CTK else tk.Label(file_frame, text="No video loaded.")
        self.lbl_file_info.grid(row=2, column=0, columnspan=2, padx=12, pady=(0, 8), sticky="w")

        # 2. Trim Settings Frame
        trim_frame = ctk.CTkFrame(self, corner_radius=10) if USE_CTK else tk.LabelFrame(self, text="Trim Segment")
        trim_frame.pack(fill="x", padx=16, pady=8)

        trim_title = ctk.CTkLabel(trim_frame, text="Time Range Selection (seconds or HH:MM:SS):", font=ctk.CTkFont(weight="bold")) if USE_CTK else tk.Label(trim_frame, text="Time Range Selection:")
        trim_title.grid(row=0, column=0, columnspan=4, padx=12, pady=(10, 6), sticky="w")

        lbl_start = ctk.CTkLabel(trim_frame, text="Start Time:") if USE_CTK else tk.Label(trim_frame, text="Start Time:")
        lbl_start.grid(row=1, column=0, padx=12, pady=4, sticky="w")
        self.entry_start = ctk.CTkEntry(trim_frame, placeholder_text="00:00:00", width=150) if USE_CTK else tk.Entry(trim_frame, width=15)
        self.entry_start.insert(0, "00:00:00")
        self.entry_start.grid(row=1, column=1, padx=4, pady=4, sticky="w")

        lbl_end = ctk.CTkLabel(trim_frame, text="End Time:") if USE_CTK else tk.Label(trim_frame, text="End Time:")
        lbl_end.grid(row=1, column=2, padx=(16, 4), pady=4, sticky="w")
        self.entry_end = ctk.CTkEntry(trim_frame, placeholder_text="End of video", width=150) if USE_CTK else tk.Entry(trim_frame, width=15)
        self.entry_end.grid(row=1, column=3, padx=4, pady=4, sticky="w")

        # 3. Output Options Frame
        out_frame = ctk.CTkFrame(self, corner_radius=10) if USE_CTK else tk.LabelFrame(self, text="Export Options")
        out_frame.pack(fill="x", padx=16, pady=8)

        self.var_export_video = tk.BooleanVar(value=True)
        self.chk_video = ctk.CTkCheckBox(out_frame, text="Export Trimmed Video", variable=self.var_export_video, command=self._toggle_video_dest) if USE_CTK else tk.Checkbutton(out_frame, text="Export Trimmed Video", variable=self.var_export_video)
        self.chk_video.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")

        self.entry_out_video = ctk.CTkEntry(out_frame, placeholder_text="Output video filepath...", width=450) if USE_CTK else tk.Entry(out_frame, width=55)
        self.entry_out_video.grid(row=1, column=0, padx=12, pady=(0, 6), sticky="ew")

        btn_browse_vid = ctk.CTkButton(out_frame, text="Save As...", width=100, command=self._browse_out_video) if USE_CTK else tk.Button(out_frame, text="Save As...", command=self._browse_out_video)
        btn_browse_vid.grid(row=1, column=1, padx=(0, 12), pady=(0, 6))

        self.var_export_audio = tk.BooleanVar(value=True)
        self.chk_audio = ctk.CTkCheckBox(out_frame, text="Extract Audio Track (.mp3)", variable=self.var_export_audio, command=self._toggle_audio_dest) if USE_CTK else tk.Checkbutton(out_frame, text="Extract Audio Track", variable=self.var_export_audio)
        self.chk_audio.grid(row=2, column=0, padx=12, pady=(6, 4), sticky="w")

        self.entry_out_audio = ctk.CTkEntry(out_frame, placeholder_text="Output audio filepath...", width=450) if USE_CTK else tk.Entry(out_frame, width=55)
        self.entry_out_audio.grid(row=3, column=0, padx=12, pady=(0, 10), sticky="ew")

        btn_browse_aud = ctk.CTkButton(out_frame, text="Save As...", width=100, command=self._browse_out_audio) if USE_CTK else tk.Button(out_frame, text="Save As...", command=self._browse_out_audio)
        btn_browse_aud.grid(row=3, column=1, padx=(0, 12), pady=(0, 10))

        out_frame.grid_columnconfigure(0, weight=1)

        # 4. Action & Log Frame
        action_frame = ctk.CTkFrame(self, corner_radius=10) if USE_CTK else tk.Frame(self)
        action_frame.pack(fill="both", expand=True, padx=16, pady=8)

        self.btn_process = (
            ctk.CTkButton(
                action_frame,
                text="🚀 Start Processing",
                font=ctk.CTkFont(size=15, weight="bold"),
                height=40,
                command=self._start_processing_thread,
            )
            if USE_CTK
            else tk.Button(action_frame, text="Start Processing", font=("Segoe UI", 12, "bold"), command=self._start_processing_thread)
        )
        self.btn_process.pack(fill="x", padx=12, pady=(10, 6))

        # Status log text
        if USE_CTK:
            self.txt_log = ctk.CTkTextbox(action_frame, height=100)
            self.txt_log.pack(fill="both", expand=True, padx=12, pady=(4, 10))
        else:
            self.txt_log = tk.Text(action_frame, height=6, bg="#202020", fg="#ffffff")
            self.txt_log.pack(fill="both", expand=True, padx=12, pady=(4, 10))

        self._log("Ready. Select a video file to begin.")

    def _log(self, message: str):
        if USE_CTK:
            self.txt_log.insert("end", message + "\n")
            self.txt_log.see("end")
        else:
            self.txt_log.insert(tk.END, message + "\n")
            self.txt_log.see(tk.END)

    def _browse_input_file(self):
        file_types = [
            ("Video Files", "*.mp4 *.mkv *.mov *.avi *.webm *.flv *.m4v"),
            ("All Files", "*.*"),
        ]
        chosen = filedialog.askopenfilename(title="Select Video File", filetypes=file_types)
        if not chosen:
            return

        self.entry_input.delete(0, "end" if USE_CTK else tk.END)
        self.entry_input.insert(0, chosen)

        # Auto-detect duration
        p = Path(chosen)
        self._log(f"Analyzing source file: {p.name}...")
        try:
            if VideoFileClip is not None:
                with VideoFileClip(str(p)) as clip:
                    self.video_duration = clip.duration or 0.0
                    info_str = f"Duration: {format_seconds(self.video_duration)} ({self.video_duration:.2f}s) | Size: {p.stat().st_size / (1024*1024):.2f} MB"
                    self.lbl_file_info.configure(text=info_str) if USE_CTK else self.lbl_file_info.config(text=info_str)
                    
                    self.entry_end.delete(0, "end" if USE_CTK else tk.END)
                    self.entry_end.insert(0, format_seconds(self.video_duration))
            else:
                self.lbl_file_info.configure(text=f"Loaded: {p.name}") if USE_CTK else self.lbl_file_info.config(text=f"Loaded: {p.name}")

            # Pre-fill default output filenames
            parent_dir = p.parent
            base_stem = p.stem
            default_vid = str(parent_dir / f"{base_stem}_trimmed.mp4")
            default_aud = str(parent_dir / f"{base_stem}_audio.mp3")

            self.entry_out_video.delete(0, "end" if USE_CTK else tk.END)
            self.entry_out_video.insert(0, default_vid)

            self.entry_out_audio.delete(0, "end" if USE_CTK else tk.END)
            self.entry_out_audio.insert(0, default_aud)

            self._log(f"File loaded successfully: {p.name}")
        except Exception as e:
            self._log(f"Notice: Could not read video metadata ({e}).")

    def _browse_out_video(self):
        chosen = filedialog.asksaveasfilename(
            title="Save Trimmed Video As",
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4"), ("All Files", "*.*")],
        )
        if chosen:
            self.entry_out_video.delete(0, "end" if USE_CTK else tk.END)
            self.entry_out_video.insert(0, chosen)

    def _browse_out_audio(self):
        chosen = filedialog.asksaveasfilename(
            title="Save Extracted Audio As",
            defaultextension=".mp3",
            filetypes=[("MP3 Audio", "*.mp3"), ("WAV Audio", "*.wav"), ("AAC Audio", "*.aac"), ("All Files", "*.*")],
        )
        if chosen:
            self.entry_out_audio.delete(0, "end" if USE_CTK else tk.END)
            self.entry_out_audio.insert(0, chosen)

    def _toggle_video_dest(self):
        state = "normal" if self.var_export_video.get() else "disabled"
        self.entry_out_video.configure(state=state) if USE_CTK else self.entry_out_video.config(state=state)

    def _toggle_audio_dest(self):
        state = "normal" if self.var_export_audio.get() else "disabled"
        self.entry_out_audio.configure(state=state) if USE_CTK else self.entry_out_audio.config(state=state)

    def _start_processing_thread(self):
        if self.is_processing:
            return

        input_file = self.entry_input.get().strip()
        if not input_file:
            messagebox.showwarning("Missing Input", "Please select a source video file.")
            return

        if not Path(input_file).exists():
            messagebox.showerror("File Not Found", f"Source video file does not exist:\n{input_file}")
            return

        do_video = self.var_export_video.get()
        do_audio = self.var_export_audio.get()

        if not do_video and not do_audio:
            messagebox.showwarning("Nothing Selected", "Please enable either video trimming or audio extraction.")
            return

        out_video = self.entry_out_video.get().strip() if do_video else None
        out_audio = self.entry_out_audio.get().strip() if do_audio else None

        start_time = self.entry_start.get().strip() or "0"
        end_time = self.entry_end.get().strip() or None

        # Validate timestamps
        try:
            st = parse_timestamp(start_time)
            et = parse_timestamp(end_time) if end_time else None
            if st < 0 or (et is not None and et < 0):
                messagebox.showerror("Invalid Time", "Timestamps cannot be negative.")
                return
            if et is not None and st >= et:
                messagebox.showerror("Invalid Range", f"Start time ({st}s) must be less than end time ({et}s).")
                return
        except Exception as e:
            messagebox.showerror("Invalid Timestamp", f"Could not parse timestamp: {e}")
            return

        self.is_processing = True
        self.btn_process.configure(state="disabled", text="⏳ Processing in progress...") if USE_CTK else self.btn_process.config(state="disabled", text="Processing...")
        self._log(f"Starting processing for '{Path(input_file).name}'...")

        # Worker thread
        thread = threading.Thread(
            target=self._run_processing,
            args=(input_file, out_video, out_audio, start_time, end_time),
            daemon=True,
        )
        thread.start()

    def _run_processing(self, input_file, out_video, out_audio, start_time, end_time):
        success = False
        try:
            success = process_video(
                input_file=input_file,
                output_video=out_video,
                output_audio=out_audio,
                start_time_str=start_time,
                end_time_str=end_time,
            )
        except Exception as e:
            self._log(f"Error occurred: {e}")

        # Update UI back on main thread
        self.after(0, self._on_processing_complete, success)

    def _on_processing_complete(self, success: bool):
        self.is_processing = False
        self.btn_process.configure(state="normal", text="🚀 Start Processing") if USE_CTK else self.btn_process.config(state="normal", text="Start Processing")
        if success:
            self._log("SUCCESS: Export completed!")
            messagebox.showinfo("Success", "Video and/or audio processed successfully!")
        else:
            self._log("FAILURE: Processing encountered errors. Check log above.")
            messagebox.showerror("Processing Failed", "Failed to process media. Check output log for details.")


def main():
    app = MediaProcessorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
