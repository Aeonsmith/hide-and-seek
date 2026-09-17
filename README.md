# Video Trimmer & Audio Extractor

A robust Python CLI tool and module built on top of [MoviePy](https://zulko.github.io/moviepy/) to trim videos and extract audio tracks with error handling and timestamp format support.

---

## Features

- **Video Trimming**: Cut segments out of videos with precise start and end timestamps.
- **Audio Extraction**: Export the extracted audio track directly to MP3 or other audio formats.
- **Flexible Timestamps**: Accepts raw seconds (`45.5`) as well as formatted strings (`MM:SS` or `HH:MM:SS`).
- **Resilient Error Handling**:
  - File existence and permission validation.
  - Video length verification and duration clamping.
  - Graceful handling of silent videos (videos without audio tracks).
  - Automatic creation of missing parent output directories.
  - Safe resource cleanup for file descriptors and subprocesses.

---

## Requirements & Installation

1. **Python**: Python 3.9+ installed.
2. **Dependencies**:
   ```bash
   pip install moviepy numpy
   ```

*(Note: MoviePy automatically manages `imageio-ffmpeg` binaries for video/audio encoding).*

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

## Examples

### 1. Basic Trim & Audio Extraction
Trim a video from `00:15` to `01:45` and export both the video and audio:
```bash
python process_video.py input.mp4 --start 00:15 --end 01:45
```

### 2. Audio-Only Extraction
Extract audio from a 30-second highlight without generating a new video file:
```bash
python process_video.py lecture.mp4 --start 00:10:00 --end 00:15:30 --no-video --out-audio lecture_clip.mp3
```

### 3. Video-Only Trim
Trim video without extracting a standalone audio file:
```bash
python process_video.py source.mov --start 5.5 --end 20.0 --no-audio --out-video output_clip.mp4
```

### 4. Custom Output Paths with Nested Folders
Directories will be automatically created if they do not exist:
```bash
python process_video.py input.mp4 --start 10 --end 30 --out-video exports/videos/clip.mp4 --out-audio exports/audio/clip.mp3
```

---

## Programmatic Usage

You can also import and use the functionality within your own Python code:

```python
from process_video import process_video

success = process_video(
    input_file="my_video.mp4",
    output_video="output/trimmed.mp4",
    output_audio="output/audio.mp3",
    start_time_str="01:30",
    end_time_str="02:45",
)

if success:
    print("Video processed successfully!")
else:
    print("Processing failed.")
```

---

## Running Tests

The test suite programmatically creates synthetic test media and tests all features and error conditions:

```bash
# Run with unittest
python -m unittest test_process_video.py -v

# Or run with pytest
pytest test_process_video.py -v
```
