#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Union

try:
    # MoviePy v1.x
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        # MoviePy v2.x
        from moviepy import VideoFileClip
    except ImportError:
        VideoFileClip = None


def parse_timestamp(time_input: Union[str, float, int]) -> float:
    """
    Parses a time value into seconds.
    Supports float/int seconds (e.g., 90, 12.5) or timestamp strings (e.g., '01:30', '00:01:30.500').
    """
    if isinstance(time_input, (int, float)):
        return float(time_input)

    time_str = str(time_input).strip()
    if not time_str:
        raise ValueError("Timestamp string cannot be empty.")

    # Check if direct numeric string
    try:
        return float(time_str)
    except ValueError:
        pass

    # Parse HH:MM:SS or MM:SS format
    parts = time_str.split(":")
    if len(parts) > 3 or len(parts) < 2:
        raise ValueError(
            f"Invalid timestamp format '{time_str}'. Expected seconds (e.g., '90') or 'HH:MM:SS' / 'MM:SS'."
        )

    try:
        parts = [float(p) for p in parts]
    except ValueError:
        raise ValueError(f"Non-numeric values in timestamp '{time_str}'.")

    if len(parts) == 2:  # MM:SS
        minutes, seconds = parts
        return minutes * 60 + seconds
    else:  # HH:MM:SS
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds


def ensure_output_directory(file_path: str) -> None:
    """Creates parent directories for the output path if they don't already exist."""
    path = Path(file_path).resolve()
    parent = path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise PermissionError(f"Cannot create output directory '{parent}': {e}")


def process_video(
    input_file: str,
    output_video: Optional[str] = None,
    output_audio: Optional[str] = None,
    start_time_str: Union[str, float] = 0.0,
    end_time_str: Optional[Union[str, float]] = None,
) -> bool:
    """
    Trims a video file and extracts its audio track with robust error handling.
    """
    if VideoFileClip is None:
        print("Error: MoviePy is not installed.", file=sys.stderr)
        return False

    input_path = Path(input_file).resolve()

    # 1. Validate input file existence and permissions
    if not input_path.exists():
        print(f"Error: Input file does not exist: '{input_file}'", file=sys.stderr)
        return False

    if not input_path.is_file():
        print(f"Error: Specified input path is not a file: '{input_file}'", file=sys.stderr)
        return False

    if not os.access(input_path, os.R_OK):
        print(f"Error: Insufficient read permissions for file: '{input_file}'", file=sys.stderr)
        return False

    # 2. Parse timestamps
    try:
        start_seconds = parse_timestamp(start_time_str)
        if start_seconds < 0:
            print("Error: Start time cannot be negative.", file=sys.stderr)
            return False
    except ValueError as e:
        print(f"Error parsing start time: {e}", file=sys.stderr)
        return False

    end_seconds = None
    if end_time_str is not None:
        try:
            end_seconds = parse_timestamp(end_time_str)
            if end_seconds < 0:
                print("Error: End time cannot be negative.", file=sys.stderr)
                return False
        except ValueError as e:
            print(f"Error parsing end time: {e}", file=sys.stderr)
            return False

    if end_seconds is not None and start_seconds >= end_seconds:
        print(
            f"Error: Start time ({start_seconds}s) must be strictly less than end time ({end_seconds}s).",
            file=sys.stderr,
        )
        return False

    # 3. Ensure output directories exist
    try:
        if output_video:
            ensure_output_directory(output_video)
        if output_audio:
            ensure_output_directory(output_audio)
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

    video_clip = None
    trimmed_clip = None

    try:
        # 4. Load video
        print(f"Loading video: '{input_path.name}'...")
        try:
            video_clip = VideoFileClip(str(input_path))
        except Exception as e:
            print(
                f"Error: Failed to open video file. The file may be corrupt or an unsupported format.\nDetails: {e}",
                file=sys.stderr,
            )
            return False

        duration = video_clip.duration
        if duration is None or duration <= 0:
            print("Error: Could not determine video duration or video is empty.", file=sys.stderr)
            return False

        print(f"Video loaded successfully. Total duration: {duration:.2f}s")

        # 5. Validate boundaries against actual video duration
        if start_seconds >= duration:
            print(
                f"Error: Start time ({start_seconds:.2f}s) exceeds total video duration ({duration:.2f}s).",
                file=sys.stderr,
            )
            return False

        if end_seconds is None:
            end_seconds = duration
        elif end_seconds > duration:
            print(
                f"Warning: Specified end time ({end_seconds:.2f}s) exceeds video duration ({duration:.2f}s). Clamping to {duration:.2f}s."
            )
            end_seconds = duration

        # 6. Trim video
        print(f"Trimming segment: {start_seconds:.2f}s -> {end_seconds:.2f}s...")
        if hasattr(video_clip, "subclipped"):
            trimmed_clip = video_clip.subclipped(start_seconds, end_seconds)
        else:
            trimmed_clip = video_clip.subclip(start_seconds, end_seconds)

        # 7. Write trimmed video file
        if output_video:
            print(f"Writing trimmed video to: '{output_video}'...")
            try:
                trimmed_clip.write_videofile(
                    output_video,
                    codec="libx264",
                    audio_codec="aac",
                    temp_audiofile=str(Path(output_video).parent / "temp_audio.m4a"),
                    remove_temp=True,
                    logger=None,
                )
                print(f"Video saved successfully: '{output_video}'")
            except Exception as e:
                print(f"Error during video export: {e}", file=sys.stderr)
                return False

        # 8. Write extracted audio file
        if output_audio:
            if trimmed_clip.audio is not None:
                print(f"Writing extracted audio to: '{output_audio}'...")
                try:
                    trimmed_clip.audio.write_audiofile(output_audio, logger=None)
                    print(f"Audio saved successfully: '{output_audio}'")
                except Exception as e:
                    print(f"Error during audio export: {e}", file=sys.stderr)
                    return False
            else:
                print("Notice: No audio track found in the input video. Audio export skipped.")

        print("Processing completed successfully.")
        return True

    except Exception as e:
        print(f"Unexpected error during processing: {e}", file=sys.stderr)
        return False

    finally:
        # 9. Clean up file handles
        if trimmed_clip is not None:
            try:
                trimmed_clip.close()
            except Exception:
                pass
        if video_clip is not None:
            try:
                video_clip.close()
            except Exception:
                pass


def main(args: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Robust CLI tool to trim videos and extract audio using MoviePy."
    )
    parser.add_argument("input", help="Path to input video file")
    parser.add_argument(
        "--start",
        default="0",
        help="Start timestamp in seconds or format 'MM:SS' / 'HH:MM:SS' (default: 0)",
    )
    parser.add_argument(
        "--end",
        default=None,
        help="End timestamp in seconds or format 'MM:SS' / 'HH:MM:SS' (default: end of video)",
    )
    parser.add_argument(
        "--out-video",
        default="trimmed_output.mp4",
        help="Path for trimmed video output (default: trimmed_output.mp4)",
    )
    parser.add_argument(
        "--out-audio",
        default="extracted_audio.mp3",
        help="Path for extracted audio output (default: extracted_audio.mp3)",
    )
    parser.add_argument(
        "--no-video",
        action="store_true",
        help="Skip exporting trimmed video (only extract audio)",
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Skip exporting audio (only trim video)",
    )

    parsed_args = parser.parse_args(args)

    out_video = None if parsed_args.no_video else parsed_args.out_video
    out_audio = None if parsed_args.no_audio else parsed_args.out_audio

    if not out_video and not out_audio:
        print("Error: Both video and audio export were disabled. Nothing to do.", file=sys.stderr)
        sys.exit(1)

    success = process_video(
        input_file=parsed_args.input,
        output_video=out_video,
        output_audio=out_audio,
        start_time_str=parsed_args.start,
        end_time_str=parsed_args.end,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
