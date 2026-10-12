import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from video_input import VideoInput


class VideoInputConfirmationTests(unittest.TestCase):
    def test_ok_dispatches_after_two_frames(self):
        motion = Mock()
        video = VideoInput(motion, infer=lambda _: {"labels": ["ok"], "names": ["OK"]})
        token = video.start()["token"]
        self.assertIsNone(video.frame(token, b"\xff\xd8x")["message"])
        self.assertIn("归位", video.frame(token, b"\xff\xd8x")["message"])
        motion.play.assert_called_once()

    def test_fist_needs_three_frames(self):
        motion = Mock()
        video = VideoInput(motion, infer=lambda _: {"labels": ["fist"], "names": ["拳头"]})
        token = video.start()["token"]
        for _ in range(2):
            self.assertIsNone(video.frame(token, b"\xff\xd8x")["message"])
        self.assertIn("后退", video.frame(token, b"\xff\xd8x")["message"])
        motion.play.assert_called_once()


if __name__ == "__main__":
    unittest.main()
