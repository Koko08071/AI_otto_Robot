"""Browser frame sessions backed by the existing gesture Python environment."""
import base64
import json
import os
from pathlib import Path
import queue
import secrets
import subprocess
import sys
import threading
import time

GESTURES = Path(__file__).resolve().parents[1] / 'gesture_recognition'
sys.path.append(str(GESTURES))
from motion_bridge import GestureDispatcher, load_actions, TARGET_ID
from recognize import StableGesture, confirmation_frames


class StudioMotion:
    def __init__(self, link, runner, get_composition):
        self.link, self.runner, self.get_composition = link, runner, get_composition

    def verify_idle(self):
        status = self.link.status()
        if not status.get("connected") or str(status.get("device_id", "")).replace(":", "").lower() != TARGET_ID:
            raise ValueError("请先连接指定机器人")
        if self.runner.status()["running"] or status.get("moving") or status.get("active") not in (None, "idle"):
            raise ValueError("机器人忙碌，当前动作已跳过")

    def play(self, program):
        with self.runner.lock:
            self.verify_idle()
            self.link.command("/api/output", {"enabled": True})
            self.link.command("/api/play", program)

    def play_composition(self, composition):
        with self.runner.lock:
            self.verify_idle()
            item = self.get_composition(composition["id"])
            if item["name"] != composition["name"]:
                raise ValueError("组合名称与映射不一致")
            self.runner.start(composition["id"], source="video")

    def stop(self):
        with self.runner.lock:
            status = self.link.status()
            if str(status.get("device_id", "")).replace(":", "").lower() != TARGET_ID:
                raise ValueError("机器人身份不匹配")
            self.runner.stop()
            self.link.command("/api/stop", {})


class VideoInput:
    def __init__(self, motion, infer=None):
        self.motion = motion
        self.lock = threading.RLock()
        self.inference_lock = threading.Lock()
        self.token = None
        self.last_frame = 0.0
        self.process = None
        self.results = queue.Queue()
        self.infer_override = infer

    def start(self):
        with self.lock:
            if self.token and time.monotonic() - self.last_frame < 15:
                raise ValueError("视频已在其他页面开启，请先关闭")
            self.token = secrets.token_urlsafe(24)
            self.last_frame = time.monotonic()
            self.stable = StableGesture(3)
            self.dispatcher = GestureDispatcher(load_actions(), self.motion)
            return {"token": self.token}

    def stop(self, token):
        with self.lock:
            if token == self.token:
                self.token = None
            return {"active": False}

    def infer(self, jpeg):
        if self.infer_override:
            return self.infer_override(jpeg)
        if self.process is None or self.process.poll() is not None:
            python = sys.executable
            self.results = queue.Queue()
            self.process = subprocess.Popen(
                [str(python), str(GESTURES / "video_worker.py")],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True, encoding="utf-8", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            def read(process, results):
                for line in process.stdout:
                    results.put(line)
                results.put('{"error":"识别进程已退出"}')
            threading.Thread(target=read, args=(self.process, self.results), daemon=True).start()
        self.process.stdin.write(json.dumps({"jpeg": base64.b64encode(jpeg).decode("ascii")}) + "\n")
        self.process.stdin.flush()
        try:
            reply = json.loads(self.results.get(timeout=45))
        except queue.Empty:
            self.process.kill()
            self.process.wait(timeout=5)
            raise ValueError("视频识别超时")
        if reply.get("error"):
            raise ValueError(reply["error"])
        return reply

    def preview(self, jpeg):
        if not jpeg.startswith(b"\xff\xd8") or len(jpeg) > 1500000:
            raise ValueError("需要不超过 1.5 MB 的 JPEG 视频帧")
        if not self.inference_lock.acquire(blocking=False):
            return {"busy": True}
        try:
            return self.infer(jpeg)
        finally:
            self.inference_lock.release()

    def frame(self, token, jpeg):
        if not jpeg.startswith(b"\xff\xd8") or len(jpeg) > 1500000:
            raise ValueError("需要不超过 1.5 MB 的 JPEG 视频帧")
        if not self.inference_lock.acquire(blocking=False):
            return {"busy": True}
        received = time.monotonic()
        try:
            with self.lock:
                if not token or token != self.token or received - self.last_frame > 15:
                    raise ValueError("视频会话已失效，请重新开启")
                self.last_frame = received
            reply = self.infer(jpeg)
            with self.lock:
                if token != self.token:
                    return {"active": False}
                self.last_frame = time.monotonic()
                if self.last_frame - received > 3:
                    self.stable = StableGesture(3)
                    return {**reply, "message": "识别较慢，等待新画面", "active": True}
                labels = tuple(sorted(set(reply["labels"])))
                required_frames = confirmation_frames(labels, self.stable.frames)
                self.stable.update(labels, required_frames)
                message = None
                if self.stable.count >= required_frames:
                    try:
                        message = self.dispatcher.dispatch(labels)
                    except Exception as exc:
                        message = str(exc)
                return {**reply, "message": message, "active": True}
        finally:
            self.inference_lock.release()
