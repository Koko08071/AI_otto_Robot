"""Repository-relative configuration; process environment overrides local JSON."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_path = ROOT / 'config.local.json'
_local = json.loads(_path.read_text(encoding='utf-8-sig')) if _path.exists() else {}

def setting(name, default=''):
    return os.environ.get(name, _local.get(name, default))

def local_path(name, default):
    path = Path(setting(name, default)).expanduser()
    return path if path.is_absolute() else ROOT / path

DEVICE_URL = setting('OTTO_DEVICE_URL', 'http://otto.local').rstrip('/')
TARGET_ID = setting('OTTO_DEVICE_ID', '14c19f300e70').replace(':', '').lower()
BLE_NAME = setting('OTTO_BLE_NAME', 'Otto-0E70')
MODEL = local_path('OTTO_GESTURE_MODEL', 'models/YOLOv10x_gestures_openvino_model')
