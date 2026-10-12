"""BLE transport; browser requests are bridged by this local process, never USB."""
import asyncio
import json
import threading
import time
from bleak import BleakClient, BleakScanner
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / 'gesture_recognition'))
from robot_config import BLE_NAME

SERVICE = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
RX = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
TX = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'

class BleTransport:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()
        self.client = None
        self.sequence = 0
        self.last_reply = None
        self.last_disconnect = None
        self.lock = threading.RLock()

    def _on_disconnected(self, _client):
        self.last_disconnect = 'BLE 设备断开或 Windows BLE 链路中断'
        print(self.last_disconnect, flush=True)

    def run(self, coroutine, timeout=20):
        future = asyncio.run_coroutine_threadsafe(coroutine, self.loop)
        try:
            return future.result(timeout)
        except Exception:
            future.cancel()
            raise

    async def _connect(self):
        if self.client and self.client.is_connected:
            return
        device = await BleakScanner.find_device_by_filter(
            lambda d, a: a.local_name == BLE_NAME and SERVICE in a.service_uuids,
            timeout=10, service_uuids=[SERVICE])
        if not device:
            raise RuntimeError(f'未发现 {BLE_NAME}，请确认机器人已开机、电脑蓝牙已开启')
        self.client = BleakClient(device, timeout=12, disconnected_callback=self._on_disconnected)
        await self.client.connect()
        self.last_disconnect = None

    def connect(self):
        with self.lock:
            self.run(self._connect(), 30)

    async def _disconnect(self):
        if self.client:
            await self.client.disconnect()
        self.client = None

    def disconnect(self):
        with self.lock:
            self.run(self._disconnect())

    def reconnect(self):
        with self.lock:
            self.run(self._disconnect())
            self.run(self._connect(), 30)

    async def _request(self, path, body):
        if not self.client or not self.client.is_connected:
            raise RuntimeError('蓝牙尚未连接')
        self.sequence += 1
        request_id = self.sequence
        packet = (json.dumps(dict(id=request_id, path=path, body=body or {}), separators=(',', ':'))+'\n').encode()
        if len(packet) > 65536:
            raise ValueError('BLE 请求超过固件 65536 字节缓冲区')
        # Reconnect after partial write failure so an incomplete frame cannot prefix the next command.
        try:
            for start in range(0, len(packet), 180):
                await self.client.write_gatt_char(RX, packet[start:start+180], response=True)
            deadline = time.monotonic()+8
            while time.monotonic() < deadline:
                reply = json.loads(bytes(await self.client.read_gatt_char(TX)))
                self.last_reply = reply
                if reply.get('id') == request_id:
                    return reply
                await asyncio.sleep(.04)
            raise TimeoutError(f'机器人蓝牙响应超时，最后响应：{reply}')
        except BaseException:
            await self._disconnect()
            raise

    def request(self, path, body=None):
        with self.lock:
            return self.run(self._request(path, body), 45)
