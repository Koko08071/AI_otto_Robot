import importlib.util
import os
from pathlib import Path
import sys
import unittest
import threading
from http.client import HTTPConnection
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web'))
import video_input
from robot_config import local_path, setting

class PortableRuntimeTests(unittest.TestCase):
    def test_custom_port_accepts_loopback_and_rejects_foreign_host(self):
        import server
        http = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        worker = threading.Thread(target=http.serve_forever, daemon=True)
        worker.start()
        try:
            for host, expected in [(f'localhost:{http.server_port}', 200), ('example.com', 403)]:
                connection = HTTPConnection('127.0.0.1', http.server_port, timeout=5)
                try:
                    connection.request('GET', '/', headers={'Host': host})
                    response = connection.getresponse()
                    self.assertEqual(response.status, expected)
                    response.read()
                finally:
                    connection.close()
        finally:
            http.shutdown()
            http.server_close()
            worker.join(timeout=5)

    def test_video_imports_repository_gestures(self):
        self.assertEqual(Path(video_input.GESTURES).resolve(), ROOT / 'gesture_recognition')
        self.assertTrue((video_input.GESTURES / 'video_worker.py').is_file())

    def test_relative_models_do_not_depend_on_working_directory(self):
        with patch.dict(os.environ, {'OTTO_GESTURE_MODEL': 'models/test'}):
            self.assertEqual(local_path('OTTO_GESTURE_MODEL', 'unused'), ROOT / 'models/test')

    def test_environment_override(self):
        with patch.dict(os.environ, {'OTTO_PORT': '9876'}):
            self.assertEqual(setting('OTTO_PORT', 8765), '9876')
