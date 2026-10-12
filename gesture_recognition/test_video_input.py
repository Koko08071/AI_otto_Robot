import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'web'))
from video_input import VideoInput, StudioMotion


class VideoTests(unittest.TestCase):
    def test_control_panel_preview_never_dispatches_motion(self):
        motion = Mock()
        video = VideoInput(motion, infer=lambda jpeg: {'labels': ['fist'], 'names': ['拳头']})
        for _ in range(5):
            self.assertEqual(video.preview(b'\xff\xd8test')['names'], ['拳头'])
        self.assertEqual(motion.mock_calls, [])

    def test_requires_three_fresh_frames_and_stop_invalidates_session(self):
        motion = Mock()
        video = VideoInput(motion, infer=lambda jpeg: {'labels': ['fist'], 'names': ['拳头']})
        token = video.start()['token']
        for _ in range(2):
            video.frame(token, b'\xff\xd8test')
        motion.play.assert_not_called()
        video.frame(token, b'\xff\xd8test')
        motion.play.assert_called_once()
        video.frame(token, b'\xff\xd8test')
        motion.play.assert_called_once()
        video.stop(token)
        with self.assertRaises(ValueError):
            video.frame(token, b'\xff\xd8test')

    def test_stop_during_inference_discards_result(self):
        entered, release = threading.Event(), threading.Event()
        def infer(jpeg):
            entered.set(); release.wait(3)
            return {'labels': ['fist'], 'names': ['拳头']}
        motion = Mock()
        video = VideoInput(motion, infer=infer)
        token = video.start()['token']
        video.stable.count = 3
        thread = threading.Thread(target=video.frame, args=(token, b'\xff\xd8test'))
        thread.start(); self.assertTrue(entered.wait(2))
        video.stop(token); release.set(); thread.join(3)
        self.assertFalse(thread.is_alive())
        motion.play.assert_not_called()

    def test_voice_composition_blocks_video_motion(self):
        link, runner = Mock(), Mock()
        runner.lock = threading.RLock()
        link.status.return_value = {'connected': True, 'device_id': '14:c1:9f:30:0e:70', 'active': 'idle'}
        runner.status.return_value = {'running': True}
        motion = StudioMotion(link, runner, Mock())
        with self.assertRaises(ValueError):
            motion.play({})
        link.command.assert_not_called()

    def test_stop_cancels_composition_scheduler(self):
        link, runner = Mock(), Mock()
        runner.lock = threading.RLock()
        link.status.return_value = {'device_id': '14:c1:9f:30:0e:70'}
        StudioMotion(link, runner, Mock()).stop()
        runner.stop.assert_called_once()
        link.command.assert_called_once_with('/api/stop', {})

    def test_second_tab_cannot_replace_active_session(self):
        video = VideoInput(Mock(), infer=Mock())
        token = video.start()['token']
        with self.assertRaises(ValueError): video.start()
        video.stop('wrong-token')
        self.assertEqual(video.token, token)


if __name__ == '__main__': unittest.main()
