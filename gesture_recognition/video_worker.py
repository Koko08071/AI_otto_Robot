"""Line-based JPEG inference worker for the local Studio server (no robot I/O)."""
import base64
import contextlib
import json
import sys


def main():
    output = sys.stdout
    with contextlib.redirect_stdout(sys.stderr):
        import cv2
        import numpy as np
        from ultralytics import YOLO
        from recognize import DEFAULT_MODEL, detections, detect_finger_gun, ZH
        model = YOLO(str(DEFAULT_MODEL))
        names = {int(i): str(name) for i, name in model.names.items()}
    for line in sys.stdin:
        try:
            payload = json.loads(line)
            jpeg = base64.b64decode(payload["jpeg"], validate=True)
            frame = cv2.imdecode(np.frombuffer(jpeg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None or max(frame.shape[:2]) > 1920:
                raise ValueError("Invalid or oversized camera frame")
            with contextlib.redirect_stdout(sys.stderr):
                result = model.predict(frame, conf=0.45, imgsz=960, verbose=False, device="cpu")[0]
            labels, _ = detections(result, names)
            gun, _ = detect_finger_gun(result, names)
            labels = sorted((set(labels) - {"point"}) | {"finger_gun"}) if gun else list(labels)
            reply = {"labels": labels, "names": ["手势枪" if x == "finger_gun" else ZH.get(x, x) for x in labels]}
        except Exception as exc:
            reply = {"error": str(exc)}
        output.write(json.dumps(reply, ensure_ascii=True) + "\n")
        output.flush()


if __name__ == "__main__":
    main()
