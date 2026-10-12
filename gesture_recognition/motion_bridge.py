"""Identity-checked HTTP control for one-shot Otto gesture actions."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

TARGET_ID = "14c19f300e70"
DEFAULT_ACTIONS = Path(__file__).with_name("gesture_actions.json")


def load_actions(path: Path = DEFAULT_ACTIONS) -> dict:
    actions = json.loads(path.read_text(encoding="utf-8"))
    for gesture in ("finger_gun", "fist", "ok"):
        program = actions[gesture]["program"]
        if not program["segments"] or program.get("repeat", False):
            raise ValueError(f"Unsafe action configuration: {gesture}")
    return actions


class RobotClient:
    def __init__(self, url: str, timeout: float = 3.0, studio_url: str | None = None):
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.studio = RobotClient(studio_url, timeout=10.0) if studio_url else None
        self.composition_active = False
        if not self.url.startswith("http://"):
            raise ValueError("Robot URL must use http:// on a trusted local network")

    def request(self, path: str, body: dict | None = None) -> dict:
        data = None if body is None else json.dumps(body, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            self.url + path,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Robot HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}") from exc

    def verify(self) -> dict:
        status = self.request("/api/status")
        device_id = str(status.get("device_id", "")).replace(":", "").lower()
        if device_id != TARGET_ID:
            raise RuntimeError(f"Robot identity mismatch: {status.get('device_id', 'missing')}")
        if not status.get("servo_available"):
            raise RuntimeError("Robot reports no servo control")
        return status

    def play(self, program: dict) -> None:
        self.check_composition_idle()
        status = self.verify()
        if status.get("active") not in (None, "idle") or status.get("moving"):
            raise RuntimeError("Robot is busy; action skipped")
        if not status.get("servo_enabled"):
            self.request("/api/output", {"enabled": True})
        self.request("/api/play", program)

    def stop(self) -> None:
        self.verify()
        if self.composition_active:
            self.studio.verify()
            self.studio.request("/api/compositions/stop", {})
            self.composition_active = False
        self.request("/api/stop", {})

    def check_composition_idle(self) -> None:
        if self.composition_active:
            if self.studio.request("/api/compositions/run").get("running"):
                raise RuntimeError("Robot composition is busy; action skipped")
            self.composition_active = False

    def play_composition(self, composition: dict) -> None:
        if self.studio is None:
            raise RuntimeError("Composition requires the local Studio service")
        self.verify()
        status = self.studio.verify()
        if not status.get("connected"):
            raise RuntimeError("Studio is not connected to the robot")
        if self.studio.request("/api/compositions/run").get("running"):
            raise RuntimeError("Robot composition is busy; action skipped")
        if status.get("moving") or status.get("active") not in (None, "idle"):
            raise RuntimeError("Robot is busy; action skipped")
        saved = self.studio.request("/api/compositions/" + composition["id"])
        if saved.get("name") != composition["name"]:
            raise RuntimeError("Saved composition name does not match configuration")
        # An HTTP timeout may occur after playback starts; retain stop routing.
        self.composition_active = True
        self.studio.request("/api/compositions/run", {"id": composition["id"]})


class GestureDispatcher:
    """Rate-limit held gestures while allowing confirmed gesture changes immediately."""

    def __init__(self, actions: dict, client: RobotClient, cooldown: float = 5.0):
        self.actions = actions
        self.client = client
        self.cooldown = cooldown
        self.next_allowed = 0.0
        self.stop_held = False
        self.last_gesture = None
        self.retry_after: dict[str, float] = {}

    def dispatch(self, gestures: tuple[str, ...], now: float | None = None) -> str | None:
        now = time.monotonic() if now is None else now
        gestures = tuple(sorted({
            "heart" if g in ("hand_heart", "hand_heart2")
            else "little_finger" if g in ("pinkie", "middle_finger", "mid.finger", "mid_finger") else g for g in gestures
        }))
        if "stop" in gestures:
            if self.stop_held:
                return None
            if now < self.retry_after.get("stop", 0.0):
                return None
            self.retry_after["stop"] = now + 2.0
            self.client.stop()
            self.stop_held = True
            self.last_gesture = "stop"
            return "stop -> 停止"
        self.stop_held = False
        matched = [gesture for gesture in gestures if gesture in self.actions]
        if len(matched) != 1:
            self.last_gesture = None
            return None
        gesture = matched[0]
        if gesture == self.last_gesture and now < self.next_allowed:
            return None
        if now < self.retry_after.get(gesture, 0.0):
            return None
        action = self.actions[gesture]
        # Failed or busy requests retry separately from successful motion timing.
        self.retry_after[gesture] = now + 2.0
        if "composition" in action:
            self.client.play_composition(action["composition"])
        else:
            self.client.play(action["program"])
        self.retry_after.pop(gesture, None)
        self.last_gesture = gesture
        self.next_allowed = now + self.cooldown
        return f"{gesture} -> {action['label']}（已发送）"
