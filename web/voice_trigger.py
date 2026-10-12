"""Two-stage wake-word and command recognition for Otto, browser mic, or FFmpeg.

Preferred capture on macOS is the webpage microphone (browser getUserMedia),
which posts PCM chunks to the local server. Robot body mic remains available.
"""
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / 'gesture_recognition'))
from robot_config import local_path
from http.client import IncompleteRead
import queue
import shutil
import subprocess
import threading
import time
import urllib.request
from urllib.parse import urlparse

WAKE_WORD = '小黄小黄'
# Aliases cover Whisper mishears seen in handoff tests (小黃→OpenCC, 小巴, contractions).
WAKE_ALIASES = (WAKE_WORD, '小巴小巴', '小黄黄', '小巴巴', '小黄', '小巴')
SAMPLE_RATE = 16000
CHUNK_BYTES = 65536
COMMAND_TIMEOUT = 8
SOURCES = ('browser', 'robot', 'computer')


def normalized(text):
    from opencc import OpenCC
    return ''.join(c for c in OpenCC('t2s').convert(text).casefold() if c.isalnum())


class VoiceListener:
    def __init__(self, link, runner, list_compositions, match_trigger):
        self.link = link
        self.runner = runner
        self.list_compositions = list_compositions
        self.match_trigger = match_trigger
        self.lock = threading.RLock()
        self.cancel = threading.Event()
        self.chunks = queue.Queue(maxsize=5)
        self.microphone_process = None
        self.state = dict(
            listening=False, source='browser', phase='idle', lastText='', lastTrigger='',
            triggerCount=0, capturedChunks=0, lastRms=0, error=None,
        )

    def status(self):
        with self.lock:
            return dict(self.state)

    def start(self, source='browser'):
        if source == 'computer' and sys.platform != 'darwin':
            raise ValueError('Windows 请使用网页麦克风或机器人麦克风')
        if source not in SOURCES:
            raise ValueError('未知麦克风来源')
        if source == 'computer' and not shutil.which('ffmpeg'):
            raise ValueError('本机 FFmpeg 麦克风需要先安装 FFmpeg')
        if not any(item.get('trigger') for item in self.list_compositions()):
            raise ValueError('请先为已保存的组合设置语音关键词')
        self.stop()
        if source == 'robot':
            if not self.link.connected or self.link.mode != 'wifi':
                self.link.connect('wifi')
            if not self.link.request('/api/status').get('mic_available'):
                raise ValueError('机器人麦克风不可用，请刷入包含麦克风驱动的固件')
        else:
            # Browser / FFmpeg can listen without the robot; face feedback needs Wi-Fi when available.
            try:
                if not self.link.connected or self.link.mode != 'wifi':
                    self.link.connect('wifi')
            except Exception:
                pass
        with self.lock:
            self.cancel = threading.Event()
            self.chunks = queue.Queue(maxsize=5)
            self.state = dict(
                listening=True, source=source, phase='loading', lastText='', lastTrigger='',
                triggerCount=0, capturedChunks=0, lastRms=0, error=None,
            )
            if source == 'robot':
                threading.Thread(target=self._capture_robot, args=(self.cancel, self.chunks), daemon=True).start()
            elif source == 'computer':
                threading.Thread(target=self._capture_computer, args=(self.cancel, self.chunks), daemon=True).start()
            # browser: webpage posts PCM via ingest()
            threading.Thread(target=self._listen, args=(self.cancel, self.chunks), daemon=True).start()
            return dict(self.state)

    def stop(self):
        with self.lock:
            self.cancel.set()
            if self.microphone_process is not None:
                self.microphone_process.terminate()
                self.microphone_process = None
            self.state['listening'] = False
            self.state['phase'] = 'idle'
            return dict(self.state)

    def ingest(self, raw):
        with self.lock:
            if not self.state['listening'] or self.state['source'] != 'browser':
                raise ValueError('当前未使用网页麦克风监听')
            chunks = self.chunks
        if not isinstance(raw, (bytes, bytearray)) or len(raw) != CHUNK_BYTES:
            raise ValueError('网页麦克风录音块长度不正确')
        self._enqueue(chunks, bytes(raw))
        return self.status()

    def _capture_robot(self, cancel, chunks):
        try:
            address = urlparse(self.link.url)
            mic_url = address.geturl() + '/api/audio/mic'
            failures = 0
            while not cancel.is_set():
                if self.runner.status()['running']:
                    cancel.wait(.1)
                    continue
                try:
                    with urllib.request.urlopen(mic_url, timeout=15) as response:
                        raw = response.read()
                    if len(raw) != CHUNK_BYTES:
                        raise RuntimeError('机器人麦克风录音长度不正确')
                except (OSError, RuntimeError, IncompleteRead) as exc:
                    failures += 1
                    if failures >= 3:
                        raise exc
                    cancel.wait(.2)
                    continue
                failures = 0
                self._enqueue(chunks, raw)
        except Exception as exc:
            if not cancel.is_set():
                with self.lock:
                    self.state['error'] = str(exc)
                    self.state['listening'] = False
                cancel.set()

    @staticmethod
    def _enqueue(chunks, raw):
        try:
            chunks.put_nowait(raw)
        except queue.Full:
            try:
                chunks.get_nowait()
            except queue.Empty:
                pass
            chunks.put_nowait(raw)

    def _show_face(self, expression):
        if self.link and self.link.connected and self.link.mode == 'wifi':
            try:
                self.link.request('/api/face', {'expression': expression})
            except Exception:
                pass

    def _capture_computer(self, cancel, chunks):
        process = None
        try:
            process = subprocess.Popen(
                ['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-f', 'avfoundation',
                 '-i', os.environ.get('OTTO_COMPUTER_MIC_INPUT', ':default'), '-ac', '1', '-ar', '16000',
                 '-f', 's16le', 'pipe:1'],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            )
            with self.lock:
                self.microphone_process = process
            while not cancel.is_set():
                raw = process.stdout.read(CHUNK_BYTES)
                if len(raw) != CHUNK_BYTES:
                    raise RuntimeError(
                        '本机 FFmpeg 麦克风没有取得音频。请在 macOS「系统设置 → 隐私与安全性 → 麦克风」'
                        '允许运行本服务的应用（终端 / Cursor），然后重启服务'
                    )
                self._enqueue(chunks, raw)
        except Exception as exc:
            if not cancel.is_set():
                with self.lock:
                    self.state['error'] = str(exc)
                    self.state['listening'] = False
                cancel.set()
        finally:
            if process is not None and process.poll() is None:
                process.terminate()
            with self.lock:
                if self.microphone_process is process:
                    self.microphone_process = None

    def _listen(self, cancel, chunks):
        try:
            import numpy as np
            from faster_whisper import WhisperModel
            bundled = local_path('OTTO_WHISPER_MODEL','voice-model/base')
            if not bundled.is_dir():
                raise RuntimeError('缺少离线语音模型，请运行 tools/download_models.py --kind voice')
            model = WhisperModel(
                str(bundled),
                device='cpu', compute_type='int8',
            )
            previous = np.empty(0, dtype=np.float32)
            wake_at = None
            with self.lock:
                self.state['phase'] = 'wake'
            while not cancel.is_set():
                try:
                    raw = chunks.get(timeout=.3)
                except queue.Empty:
                    continue
                current = np.frombuffer(raw, dtype='<i2').astype(np.float32) / 32768
                with self.lock:
                    self.state['capturedChunks'] += 1
                    self.state['lastRms'] = round(float(np.sqrt(np.mean(current * current))), 4)
                if self.runner.status()['running']:
                    previous = np.empty(0, dtype=np.float32)
                    wake_at = None
                    with self.lock:
                        self.state['phase'] = 'wake'
                    continue
                if wake_at and time.monotonic() - wake_at > COMMAND_TIMEOUT:
                    wake_at = None
                    with self.lock:
                        self.state['phase'] = 'wake'
                    self._show_face('smile_static')
                audio = np.concatenate((previous, current))
                audio -= audio.mean()
                previous = current[-12000:]
                segments, _ = model.transcribe(
                    audio, language='zh', beam_size=5, condition_on_previous_text=False, vad_filter=True,
                )
                transcript = ''.join(segment.text for segment in segments).strip()
                if not transcript:
                    continue
                with self.lock:
                    self.state['lastText'] = transcript
                heard = normalized(transcript)
                if wake_at is None:
                    at = -1
                    matched = ''
                    for alias in WAKE_ALIASES:
                        at = heard.find(alias)
                        if at >= 0:
                            matched = alias
                            break
                    if at < 0:
                        continue
                    with self.lock:
                        self.state['phase'] = 'command'
                    self._show_face('question_05s')
                    wake_at = time.monotonic()
                    heard = heard[at + len(matched):]
                    if not heard:
                        continue
                item = self.match_trigger(heard, self.list_compositions())
                if not item:
                    continue
                with self.lock:
                    self.state['lastTrigger'] = item['name']
                    self.state['triggerCount'] += 1
                    self.state['phase'] = 'wake'
                self.runner.start(item['id'], source='voice')
                wake_at = None
                previous = np.empty(0, dtype=np.float32)
        except Exception as exc:
            if not cancel.is_set():
                with self.lock:
                    self.state['error'] = str(exc)
        finally:
            with self.lock:
                if self.cancel is cancel:
                    self.state['listening'] = False
                    self.state['phase'] = 'idle'
