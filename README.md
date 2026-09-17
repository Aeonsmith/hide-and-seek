# Hide and Seek — Video Trimmer & Audio Extractor

A standalone native desktop application, CLI tool, and Python module built on top of [MoviePy](https://zulko.github.io/moviepy/) to trim videos and extract audio tracks with error handling and timestamp format support.

---

## Features

- **Native Desktop GUI (No Browser)**: Sleek, responsive GUI with dark mode styling, real-time metadata inspector, file dialog pickers, and asynchronous background processing.
- **Standalone Windows Executable**: Single `.exe` binary package ready to launch from your Desktop or Start Menu without requiring a browser or terminal.
- **Video Trimming**: Cut segments out of videos with precise start and end timestamps.
- **Audio Extraction**: Export extracted audio tracks directly to MP3 or other audio formats.
- **Flexible Timestamps**: Accepts raw seconds (`45.5`) as well as formatted strings (`MM:SS` or `HH:MM:SS`).
- **Resilient Error Handling**:
  - File existence and permission validation.
  - Video length verification and duration clamping.
  - Graceful handling of silent videos (videos without audio tracks).
  - Automatic creation of missing parent output directories.
  - Safe resource cleanup for file descriptors and subprocesses.

---

## Desktop App Launching

### Launch via Desktop Shortcut
Double-click the **Hide and Seek** shortcut placed on your Windows Desktop:
```text
C:\Users\ole_a\Desktop\Hide and Seek.lnk
```

### Launch via Executable Binary
```powershell
.\dist\HideAndSeek.exe
```

### Launch GUI from Python
```powershell
python app_gui.py
```

---

## CLI Usage

Run `process_video.py` directly from your terminal:

```bash
python process_video.py <input_file> [options]
```

### Options & Arguments

| Option / Argument | Description | Default |
| :--- | :--- | :--- |
| `input` | Path to the source video file (**required**). | — |
| `--start` | Start timestamp (seconds, `MM:SS`, or `HH:MM:SS`). | `0` |
| `--end` | End timestamp (seconds, `MM:SS`, or `HH:MM:SS`). | End of video |
| `--out-video` | Destination filepath for the trimmed video. | `trimmed_output.mp4` |
| `--out-audio` | Destination filepath for the extracted audio. | `extracted_audio.mp3` |
| `--no-video` | Skip video rendering (extract audio only). | `False` |
| `--no-audio` | Skip audio extraction (trim video only). | `False` |
| `-h`, `--help` | Show help message and exit. | — |

---

## CLI Examples

### 1. Basic Trim & Audio Extraction
```bash
python process_video.py input.mp4 --start 00:15 --end 01:45
```

### 2. Audio-Only Extraction
```bash
python process_video.py lecture.mp4 --start 00:10:00 --end 00:15:30 --no-video --out-audio lecture_clip.mp3
```

### 3. Video-Only Trim
```bash
python process_video.py source.mov --start 5.5 --end 20.0 --no-audio --out-video output_clip.mp4
```

---

## Building from Source

To regenerate the multi-resolution `.ico` file and compile the standalone executable:

```powershell
# 1. Generate icon
python build_icon.py

# 2. Build executable
python -m PyInstaller --noconsole --onefile --icon=icon.ico --name="HideAndSeek" --add-data "icon.ico;." app_gui.py
```

---

## Running Tests

```powershell
# Run with unittest
python -m unittest test_process_video.py -v

# Or run with pytest
pytest test_process_video.py -v
```
