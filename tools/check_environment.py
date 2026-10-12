"""Report missing runtime resources; no device connection or motion."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'gesture_recognition'))
from robot_config import MODEL, local_path

def main():
    missing = []
    for module in ['bleak', 'faster_whisper', 'numpy', 'opencc', 'cv2', 'ultralytics', 'openvino', 'PIL', 'imageio_ffmpeg']:
        if importlib.util.find_spec(module) is None:
            missing.append(f'Python dependency: {module}')
    for name, path in [('gesture model', MODEL), ('voice model', local_path('OTTO_WHISPER_MODEL','voice-model/base'))]:
        if not path.exists():
            missing.append(f'{name}: {path}')
    audio = set()
    for path in (ROOT / 'web/library/compositions').glob('*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        for track in data.get('tracks', []):
            for clip in track.get('clips', []):
                url = clip.get('resourceSnapshot', {}).get('url', '')
                if url and not (ROOT / 'web/library/audio' / url.rsplit('/', 1)[-1]).is_file():
                    audio.add(url.rsplit('/', 1)[-1])
    if audio:
        missing.append(f'{len(audio)} referenced audio files: import your resource ZIP or replace clips')
    print('\n'.join(missing) if missing else 'All checked runtime dependencies and resources are available.')
    return 1 if missing else 0

if __name__ == '__main__':
    raise SystemExit(main())
