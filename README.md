# 🎬 Hide and Seek — Video Trimmer & Audio Extractor

[![GitHub Repository](https://img.shields.io/badge/GitHub-Aeonsmith%2Fhide--and--seek-blue?logo=github)](https://github.com/Aeonsmith/hide-and-seek)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Hide and Seek** is a standalone native desktop application, CLI tool, and Python module built on top of [MoviePy](https://zulko.github.io/moviepy/) to trim videos and extract audio tracks with precision, timestamp parsing, and robust error handling.

---

## 📌 Features

- **Native Desktop GUI (No Browser Required)**: Modern dark-themed GUI built with CustomTkinter/Tkinter featuring live file analysis, duration inspection, and background asynchronous processing.
- **Single-File Windows Executable**: Pre-packaged `.exe` binary ready to launch from your Desktop or Start Menu.
- **Precision Video Trimming**: Cut video segments using seconds (`45.5`) or timestamp strings (`MM:SS` / `HH:MM:SS`).
- **High-Quality Audio Extraction**: Extract audio tracks directly to MP3, WAV, or AAC.
- **Resilient Error Handling**:
  - Validates file existence, format compatibility, and read/write permissions.
  - Automatically verifies video length and clamps out-of-bounds timestamps.
  - Safely handles silent/audio-less video files without crashing.
  - Automatically creates missing parent directories for export destinations.
  - Guarantees file handle and resource cleanup on completion or failure.

---

## 📂 Repository Structure

```text
hide-and-seek/
├── process_video.py       # Core media processing engine & CLI interface
├── app_gui.py             # Native desktop GUI application
├── test_process_video.py  # Automated unit & integration test suite
├── build_icon.py          # Multi-resolution icon (.ico) generator
├── icon.ico               # Application icon (16x16 to 256x256)
├── HideAndSeek.spec       # PyInstaller build specification
├── README.md              # Project documentation
└── dist/
    └── HideAndSeek.exe    # Standalone compiled Windows executable
```

---

## ⚙️ Prerequisites & Installation

### Option 1: Running the Pre-compiled Executable (No Python Required)
You can launch the compiled `.exe` directly without installing Python dependencies:
- **Desktop Shortcut**: `C:\Users\ole_a\Desktop\Hide and Seek.lnk`
- **Direct Binary**: `.\dist\HideAndSeek.exe`

### Option 2: Running from Source
If running from source, ensure you have Python 3.9+ installed, then install the required dependencies:

```bash
pip install moviepy numpy customtkinter pillow pyinstaller
```

*(Note: MoviePy automatically manages `imageio-ffmpeg` binaries for encoding/decoding).*

---

## 🖥️ Desktop GUI Usage

Launch the GUI via Python:
```bash
python app_gui.py
```

### GUI Features:
1. **Browse Source**: Select any video file (`.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`).
2. **Auto Metadata**: Automatically displays the total duration, file size, and pre-populates default output paths.
3. **Select Range**: Enter start/end timestamps (e.g., `00:00:15` to `00:01:30` or `15` to `90`).
4. **Export Options**: Toggle video trimming and audio extraction independently.
5. **Start Processing**: Runs in a background thread to keep the interface responsive, showing live status logs.

---

## ⌨️ CLI Usage

Run `process_video.py` directly from your command line:

```bash
python process_video.py <input_file> [options]
```

### CLI Arguments & Options

| Option / Flag | Description | Default |
| :--- | :--- | :--- |
| `input` | Path to the source video file (**required**). | — |
| `--start` | Start timestamp (`float` seconds, `MM:SS`, or `HH:MM:SS`). | `0` |
| `--end` | End timestamp (`float` seconds, `MM:SS`, or `HH:MM:SS`). | End of video |
| `--out-video` | Destination path for trimmed video output. | `trimmed_output.mp4` |
| `--out-audio` | Destination path for extracted audio output. | `extracted_audio.mp3` |
| `--no-video` | Skip video rendering (extract audio only). | `False` |
| `--no-audio` | Skip audio extraction (trim video only). | `False` |
| `-h`, `--help` | Display help message and exit. | — |

---

## 💡 Usage Examples

### 1. Basic Trim & Audio Extraction
Trim a video from `00:15` to `01:45` and export both the video and audio tracks:
```bash
python process_video.py input.mp4 --start 00:15 --end 01:45
```

### 2. Audio-Only Extraction
Extract audio from a specific 5-minute section without re-encoding video:
```bash
python process_video.py lecture.mp4 --start 00:10:00 --end 00:15:00 --no-video --out-audio lecture_clip.mp3
```

### 3. Video-Only Trim
Trim video using exact float seconds and suppress audio extraction:
```bash
python process_video.py highlight.mov --start 12.5 --end 45.0 --no-audio --out-video clip.mp4
```

### 4. Custom Output Directory
Automatically create nested destination directories if they don't exist:
```bash
python process_video.py input.mp4 --start 10 --end 30 --out-video exports/videos/trimmed.mp4 --out-audio exports/audio/track.mp3
```

---

## 🐍 Programmatic Python API

You can import `process_video` and `parse_timestamp` directly into your own Python applications:

```python
from process_video import parse_timestamp, process_video

# 1. Parse timestamps into seconds
start_sec = parse_timestamp("01:30")  # Returns 90.0
end_sec = parse_timestamp("00:03:15") # Returns 195.0

# 2. Process video
success = process_video(
    input_file="raw_recording.mp4",
    output_video="exports/highlight.mp4",
    output_audio="exports/highlight_audio.mp3",
    start_time_str="01:30",
    end_time_str="03:15",
)

if success:
    print("Export completed successfully!")
else:
    print("Processing failed.")
```

---

## 🧪 Running the Test Suite

The test suite uses `unittest` and programmatically creates synthetic test media (video and audio sine waves) in temporary directories without requiring external files:

```bash
# Run with Python's built-in test runner
python -m unittest test_process_video.py -v

# Or run with pytest
pytest test_process_video.py -v
```

---

## 🔨 Building & Packaging from Source

To regenerate the multi-resolution `.ico` icon and compile the standalone executable:

```powershell
# 1. Generate multi-resolution icon (16x16 up to 256x256)
python build_icon.py

# 2. Build single-file GUI executable
python -m PyInstaller --noconsole --onefile --icon=icon.ico --name="HideAndSeek" --add-data "icon.ico;." app_gui.py
```

The compiled binary will be placed in the `dist/` directory.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
