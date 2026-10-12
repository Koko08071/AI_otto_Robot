"""Download upstream models separately from Git; never send robot commands."""
import argparse
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=['gesture', 'voice', 'all'], default='all')
    args = parser.parse_args()
    if args.kind in ('gesture', 'all'):
        from ultralytics import YOLO
        target = ROOT / 'models/YOLOv10x_gestures.pt'
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            partial = target.with_suffix('.download')
            try:
                print('Downloading HaGRID YOLOv10x (~255 MB)', flush=True)
                urllib.request.urlretrieve('https://rndml-team-cv.obs.ru-moscow-1.hc.sbercloud.ru/datasets/hagrid_v2/models/YOLOv10x_gestures.pt', partial)
                partial.replace(target)
            finally:
                partial.unlink(missing_ok=True)
        YOLO(str(target)).export(format='openvino', imgsz=960, dynamic=True)
    if args.kind in ('voice', 'all'):
        from huggingface_hub import snapshot_download
        snapshot_download('Systran/faster-whisper-base', local_dir=ROOT / 'voice-model/base')

if __name__ == '__main__':
    main()
