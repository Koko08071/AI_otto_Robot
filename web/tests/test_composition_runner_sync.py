#!/usr/bin/env python3
"""CompositionRunner must start robot audio before motions at the same timestamp."""
from __future__ import annotations
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server


class CompositionRunnerSyncTest(unittest.TestCase):
    def test_audio_primes_before_motion_and_rebases_clock(self):
        runner = server.CompositionRunner()
        order = []
        upload_delay = 0.05

        def fake_play_audio(filename, duration_ms=None):
            order.append(('audio_upload_begin', time.monotonic(), filename, duration_ms))
            time.sleep(upload_delay)
            order.append(('audio_playing', time.monotonic()))
            return {'accepted': True}

        def fake_command(path, body):
            order.append(('command', time.monotonic(), path, body.get('name') if isinstance(body, dict) else None))
            return {'ok': True}

        item = {
            'durationMs': 200,
            'tracks': [
                {
                    'kind': 'motion', 'muted': False,
                    'clips': [{
                        'startMs': 0, 'durationMs': 200, 'muted': False,
                        'resourceId': 'swing_p500',
                        'resourceSnapshot': {
                            'url': '',
                            'program': {'name': 'swing_p500', 'segments': [{'type': 'hold', 'duration': 200}]},
                        },
                    }],
                },
                {
                    'kind': 'audio', 'muted': False,
                    'clips': [{
                        'startMs': 0, 'durationMs': 200, 'muted': False,
                        'resourceId': 'song',
                        'resourceSnapshot': {'url': '/api/audio/song.wav'},
                    }],
                },
                {'kind': 'expression', 'muted': False, 'clips': []},
                {'kind': 'music', 'muted': False, 'clips': []},
            ],
        }

        with patch.object(server.LINK, 'play_audio', side_effect=fake_play_audio), \
             patch.object(server.LINK, 'command', side_effect=fake_command), \
             patch.object(server.LINK, 'connected', True):
            runner.robot_required = True
            cancel = runner.cancel
            t0 = time.monotonic()
            runner._run(item, cancel)
            elapsed = time.monotonic() - t0

        kinds = [e[0] for e in order]
        self.assertEqual(kinds[0], 'audio_upload_begin')
        self.assertIn('audio_playing', kinds)
        self.assertIn('command', kinds)
        # Motions must not start until audio upload finished.
        play_idx = kinds.index('audio_playing')
        first_cmd = next(i for i, k in enumerate(kinds) if k == 'command')
        self.assertGreater(first_cmd, play_idx)
        # Timeline wait should be ~duration after rebase, not duration+upload.
        self.assertLess(elapsed, upload_delay + 0.35)
        # First motion command shortly after audio started playing.
        audio_t = order[play_idx][1]
        cmd_t = order[first_cmd][1]
        self.assertLess(cmd_t - audio_t, 0.05)


if __name__ == '__main__':
    unittest.main()
