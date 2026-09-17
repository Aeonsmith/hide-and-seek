import os
import shutil
import tempfile
import unittest
import numpy as np

try:
    # MoviePy v1.x
    from moviepy.editor import ColorClip, AudioClip, AudioArrayClip, VideoFileClip
except ImportError:
    # MoviePy v2.x
    from moviepy import ColorClip, AudioClip, AudioArrayClip, VideoFileClip

from process_video import parse_timestamp, process_video


class TestVideoProcessing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create a temporary workspace and generate synthetic test media."""
        cls.test_dir = tempfile.mkdtemp(prefix="video_test_")

        cls.sample_video_with_audio = os.path.join(cls.test_dir, "sample_with_audio.mp4")
        cls.sample_video_no_audio = os.path.join(cls.test_dir, "sample_no_audio.mp4")

        # 1. Generate 5-second synthetic color video (320x240, 24 fps)
        color_clip = ColorClip(size=(320, 240), color=(0, 128, 255), duration=5.0)

        # 2. Generate a 440 Hz sine wave audio tone
        samplerate = 44100
        try:
            audio_func = lambda t: np.sin(2 * np.pi * 440 * t)
            audio_clip = AudioClip(audio_func, duration=5.0, fps=samplerate)
        except Exception:
            t = np.linspace(0, 5.0, int(samplerate * 5.0), endpoint=False)
            audio_array = (np.sin(2 * np.pi * 440 * t) * 0.5)[:, np.newaxis]
            audio_clip = AudioArrayClip(audio_array, fps=samplerate)

        # Write video with audio
        if hasattr(color_clip, "set_audio"):
            video_with_audio = color_clip.set_audio(audio_clip)
        else:
            video_with_audio = color_clip.with_audio(audio_clip)

        video_with_audio.write_videofile(
            cls.sample_video_with_audio,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        )

        # Write video without audio
        color_clip.write_videofile(
            cls.sample_video_no_audio,
            fps=24,
            codec="libx264",
            logger=None,
        )

        # Close generator clips
        color_clip.close()
        video_with_audio.close()

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary test directory."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Unit Tests: Timestamp Parsing
    # -------------------------------------------------------------------------

    def test_parse_timestamp_numeric(self):
        self.assertEqual(parse_timestamp(15), 15.0)
        self.assertEqual(parse_timestamp("12.5"), 12.5)

    def test_parse_timestamp_formatted_strings(self):
        self.assertEqual(parse_timestamp("01:30"), 90.0)
        self.assertEqual(parse_timestamp("01:00:10"), 3610.0)

    def test_parse_timestamp_invalid(self):
        with self.assertRaises(ValueError):
            parse_timestamp("invalid_time")
        with self.assertRaises(ValueError):
            parse_timestamp("01:02:03:04")

    # -------------------------------------------------------------------------
    # Integration Tests: Trimming & Audio Extraction
    # -------------------------------------------------------------------------

    def test_successful_trim_and_audio_extraction(self):
        """Test trimming a 5s clip down to 2s (from 1s to 3s) and extracting audio."""
        out_video = os.path.join(self.test_dir, "trimmed_output.mp4")
        out_audio = os.path.join(self.test_dir, "extracted_output.mp3")

        success = process_video(
            input_file=self.sample_video_with_audio,
            output_video=out_video,
            output_audio=out_audio,
            start_time_str="00:01",  # 1s
            end_time_str="00:03",    # 3s
        )

        self.assertTrue(success, "Video processing should return True")
        self.assertTrue(os.path.exists(out_video), "Trimmed video file should exist")
        self.assertTrue(os.path.exists(out_audio), "Extracted audio file should exist")
        self.assertGreater(os.path.getsize(out_video), 0, "Video file should not be empty")
        self.assertGreater(os.path.getsize(out_audio), 0, "Audio file should not be empty")

        # Verify duration of output video
        with VideoFileClip(out_video) as clip:
            self.assertAlmostEqual(clip.duration, 2.0, delta=0.2)

    def test_video_without_audio_handling(self):
        """Ensure processing videos without audio completes safely without crashing."""
        out_video = os.path.join(self.test_dir, "silent_trimmed.mp4")
        out_audio = os.path.join(self.test_dir, "silent_audio.mp3")

        success = process_video(
            input_file=self.sample_video_no_audio,
            output_video=out_video,
            output_audio=out_audio,
            start_time_str=0.0,
            end_time_str=2.0,
        )

        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_video))
        # Audio file should not be created for silent video
        self.assertFalse(os.path.exists(out_audio))

    def test_nested_output_directory_creation(self):
        """Test that missing target directories are automatically created."""
        nested_video = os.path.join(self.test_dir, "nested", "subfolder", "out.mp4")
        nested_audio = os.path.join(self.test_dir, "nested", "subfolder", "out.mp3")

        success = process_video(
            input_file=self.sample_video_with_audio,
            output_video=nested_video,
            output_audio=nested_audio,
            start_time_str=0.0,
            end_time_str=1.0,
        )

        self.assertTrue(success)
        self.assertTrue(os.path.exists(nested_video))
        self.assertTrue(os.path.exists(nested_audio))

    # -------------------------------------------------------------------------
    # Edge Cases & Validation Failures
    # -------------------------------------------------------------------------

    def test_nonexistent_input_file(self):
        """Ensure failure when given a non-existent file."""
        success = process_video(
            input_file=os.path.join(self.test_dir, "does_not_exist.mp4"),
            output_video=os.path.join(self.test_dir, "out.mp4"),
        )
        self.assertFalse(success)

    def test_start_greater_than_end(self):
        """Ensure failure when start_time >= end_time."""
        success = process_video(
            input_file=self.sample_video_with_audio,
            output_video=os.path.join(self.test_dir, "out.mp4"),
            start_time_str=4.0,
            end_time_str=2.0,
        )
        self.assertFalse(success)

    def test_start_time_exceeds_duration(self):
        """Ensure failure when start_time exceeds total duration."""
        success = process_video(
            input_file=self.sample_video_with_audio,
            output_video=os.path.join(self.test_dir, "out.mp4"),
            start_time_str=10.0,  # Video is only 5s
        )
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main(verbosity=2)
