import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import RequestError, RobotLink


class BleRecoveryTests(unittest.TestCase):
    def link(self):
        link = RobotLink.__new__(RobotLink)
        link.mode = 'ble'
        link.ble = Mock()
        link.lock = threading.RLock()
        link.url = 'http://unused'
        link.connected = True
        link.last_pose = {'ll': 90, 'rl': 90, 'lf': 100, 'rf': 90}
        link.last_error = None
        return link

    def test_status_read_reconnects_once_without_resending_motion(self):
        link = self.link()
        calls = []

        def request(path):
            calls.append(path)
            if len(calls) == 1:
                link.connected = False
                raise RequestError('BLE read aborted', 503)
            return {'pose': [90, 90, 100, 90], 'device_id': '14:C1:9F:30:0E:70'}

        link.request = request
        status = link.status()
        self.assertTrue(status['connected'])
        self.assertIsNone(status['error'])
        self.assertEqual(calls, ['/api/status', '/api/status'])
        link.ble.reconnect.assert_called_once_with()

    def test_failed_reconnect_reports_disconnected(self):
        link = self.link()
        link.request = Mock(side_effect=RequestError('BLE read aborted', 503))
        link.ble.reconnect.side_effect = RuntimeError('adapter unavailable')
        status = link.status()
        self.assertFalse(status['connected'])
        self.assertIn('adapter unavailable', status['error'])
        link.request.assert_called_once_with('/api/status')

    def test_explicit_disconnect_is_not_retried(self):
        link = self.link()
        link.connected = False
        link.request = Mock()
        self.assertFalse(link.status()['connected'])
        link.ble.reconnect.assert_not_called()
        link.request.assert_not_called()


if __name__ == '__main__':
    unittest.main()
