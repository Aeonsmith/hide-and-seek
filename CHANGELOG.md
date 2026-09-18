# Changelog

All notable changes to **Hide and Seek** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-09-18

### Added
- **Native Desktop GUI Application (`app_gui.py`)**:
  - Dark-mode user interface built with CustomTkinter and Tkinter.
  - Video source browsing with automatic duration, file size, and metadata inspection.
  - Interactive start/end timestamp controls and export format toggles.
  - Asynchronous background worker threads for non-blocking video rendering.
  - Live console status log and completion alerts.
- **Standalone Windows Executable (`HideAndSeek.exe`)**:
  - Single-file binary compiled via PyInstaller with embedded assets.
  - Desktop shortcut integration with custom application icon (`icon.ico`).
- **Core Video & Audio Engine (`process_video.py`)**:
  - Precision video trimming with boundary validation, duration checks, and automatic time-clamping.
  - Dedicated audio track extraction to MP3, WAV, or AAC.
  - Flexible timestamp parsing supporting raw seconds (`45.5`), `MM:SS`, and `HH:MM:SS` formats.
  - Safe handling of silent videos (videos without audio streams).
  - Automatic parent directory creation for output files.
  - File descriptor and resource management using context managers and `try...finally` cleanup.
- **Command-Line Interface (CLI)**:
  - Command-line arguments: `--start`, `--end`, `--out-video`, `--out-audio`, `--no-video`, and `--no-audio`.
  - Full programmatic Python API support.
- **Automated Test Suite (`test_process_video.py`)**:
  - Programmatic generation of synthetic video clips and sine-wave audio tracks in temporary directories.
  - 100% test coverage for trimming, extraction, timestamp parsing, directory auto-creation, and validation error cases.
- **Packaging & Branding Assets**:
  - Multi-resolution icon generator (`build_icon.py`) producing 16x16 to 256x256 `.ico` artwork.
  - PyInstaller build configuration (`HideAndSeek.spec`).
