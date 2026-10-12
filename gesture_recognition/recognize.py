"""Run the pretrained HaGRIDv2 YOLO gesture detector on a laptop camera."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from motion_bridge import GestureDispatcher, RobotClient, load_actions

from robot_config import MODEL, DEVICE_URL, setting

DEFAULT_MODEL = MODEL

ZH = {
    "grabbing": "抓取", "grip": "握持", "holy": "双手合拢",
    "point": "指向", "call": "打电话", "three3": "三指(形态3)",
    "timeout": "暂停/T", "xsign": "交叉手势", "hand_heart": "双手比心",
    "hand_heart2": "双手比心(变体)", "little_finger": "小拇指", "pinkie": "小拇指",
    "middle_finger": "中指", "take_picture": "拍照手势",
    "dislike": "倒赞", "fist": "拳头", "four": "四指",
    "like": "点赞", "mute": "安静", "ok": "OK",
    "one": "数字一", "palm": "张开手掌", "peace": "V字/胜利",
    "peace_inverted": "反向V字", "rock": "摇滚手势",
    "stop": "停止", "stop_inverted": "反向停止",
    "three": "三指", "three2": "三指(变体2)",
    "two_up": "向上两指", "two_up_inverted": "反向向上两指",
    "three_gun": "三指枪形", "thumb_index": "拇指食指手势",
    "thumb_index2": "拇指食指手势(变体)", "no_gesture": "无指定手势",
}


def print_classes(names: dict[int, str]) -> None:
    print(f"模型实际包含 {len(names)} 个类别：", flush=True)
    for index, name in sorted(names.items()):
        print(f"  {index:2d}  {name:<20} {ZH.get(name, '未翻译')}", flush=True)
    print("注意：three_gun 是数据集定义的“三指枪形”，不等同于所有食指+拇指的手枪姿势。", flush=True)


class StableGesture:
    """Emit transitions only after several matching frames."""

    def __init__(self, frames: int):
        if frames < 1:
            raise ValueError("frames must be >= 1")
        self.frames = frames
        self.candidate: tuple[str, ...] = ()
        self.count = 0
        self.current: tuple[str, ...] = ()

    def update(self, gestures: tuple[str, ...], required_frames: int | None = None) -> bool:
        if gestures == self.candidate:
            self.count += 1
        else:
            self.candidate, self.count = gestures, 1
        if self.count >= (self.frames if required_frames is None else required_frames) and gestures != self.current:
            self.current = gestures
            return True
        return False


def confirmation_frames(gestures: tuple[str, ...], frames: int) -> int:
    if len(gestures) > 1 or any(name in gestures for name in ("fist", "finger_gun")):
        return frames
    return max(1, frames - 1)


def detections(result, names: dict[int, str]) -> tuple[tuple[str, ...], dict[str, float]]:
    scores: dict[str, float] = {}
    for label, confidence, _ in _selected_boxes(result, names):
        scores[label] = max(scores.get(label, 0.0), confidence)
    return tuple(sorted(scores)), scores


def _box_iou(left: list[float], right: list[float]) -> float:
    x1 = max(left[0], right[0])
    y1 = max(left[1], right[1])
    x2 = min(left[2], right[2])
    y2 = min(left[3], right[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    left_area = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    right_area = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union else 0.0


def _selected_boxes(result, names: dict[int, str]):
    if result.boxes is None:
        return []

    classes = result.boxes.cls.tolist()
    confidences = result.boxes.conf.tolist()
    coordinates = None
    try:
        candidate_coordinates = result.boxes.xyxy.tolist()
        if isinstance(candidate_coordinates, list) and len(candidate_coordinates) == len(classes):
            coordinates = candidate_coordinates
    except (AttributeError, TypeError):
        pass

    candidates = [
        (names[int(cls)], float(conf), coordinates[index] if coordinates is not None else None)
        for index, (cls, conf) in enumerate(zip(classes, confidences))
        if names[int(cls)] != "no_gesture"
    ]
    if coordinates is None:
        return candidates

    candidates.sort(key=lambda item: item[1], reverse=True)
    selected: list[tuple[str, float, list[float] | None]] = []
    for candidate in candidates:
        if any(_box_iou(candidate[2], item[2]) >= 0.35 for item in selected):
            continue
        selected.append(candidate)
    return selected


def detect_finger_gun(
    result,
    names: dict[int, str],
    min_confidence: float = 0.65,
) -> tuple[bool, float]:
    """Map the model's point gesture to the application's camera-facing gun gesture."""
    point_boxes = [
        (confidence, box)
        for label, confidence, box in _selected_boxes(result, names)
        if label == "point"
    ]
    point_scores = [
        confidence for confidence, _ in point_boxes
        if confidence >= min_confidence
    ]
    if point_scores:
        return True, max(point_scores)
    return False, 0.0


def draw_action_labels(cv2, frame, labels: tuple[str, ...]):
    """Draw detected action names in green Chinese text in the preview."""
    if not labels:
        return frame

    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    font_path = r"C:\Windows\Fonts\msyh.ttc"
    try:
        font = ImageFont.truetype(font_path, 28)
    except OSError:
        return frame

    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image)
    for index, label in enumerate(labels):
        name = "手势枪" if label == "finger_gun" else ZH.get(label, label)
        y = 12 + index * 38
        draw.text((18, y), name, font=font, fill=(0, 255, 0), stroke_width=2, stroke_fill=(0, 0, 0))
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)


def open_camera(cv2, index: int):
    camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera.release()
        camera = cv2.VideoCapture(index)
    return camera


def infer(model, frame, confidence, image_size):
    return model.predict(
        frame,
        conf=confidence,
        imgsz=image_size,
        verbose=False,
        device="cpu",
    )[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="HaGRIDv2 YOLO hand gesture recognition")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--camera", type=int, default=0, help="camera index, default 0")
    parser.add_argument("--conf", type=float, default=0.45, help="minimum confidence")
    parser.add_argument(
        "--gun-conf",
        type=float,
        default=0.65,
        help="minimum point confidence to trigger finger gun",
    )
    parser.add_argument("--imgsz", type=int, default=960, help="inference size, larger helps distant hands")
    parser.add_argument("--stable-frames", type=int, default=3, help="matching frames before output")
    parser.add_argument("--execute", action="store_true", help="send recognized gestures to the verified robot")
    parser.add_argument("--robot-url", default=DEVICE_URL, help="robot LAN HTTP address")
    parser.add_argument("--studio-url", default=f"http://127.0.0.1:{setting('OTTO_PORT', 8765)}", help="local composition service")
    parser.add_argument("--cooldown", type=float, default=5.0, help="seconds between repeats of the same held gesture")
    parser.add_argument("--no-preview", action="store_true", help="print to terminal without preview window")
    parser.add_argument("--list", action="store_true", help="list actual model classes and exit")
    args = parser.parse_args()
    if not args.model.is_file() and not args.model.is_dir():
        parser.error(f"model not found: {args.model}")
    if not 0 < args.conf <= 1:
        parser.error("--conf must be in (0, 1]")
    if not 0 < args.gun_conf <= 1:
        parser.error("--gun-conf must be in (0, 1]")
    if args.imgsz < 320:
        parser.error("--imgsz must be >= 320")
    if args.stable_frames < 1:
        parser.error("--stable-frames must be >= 1")
    if args.cooldown < 0:
        parser.error("--cooldown must be >= 0")

    import cv2
    from ultralytics import YOLO

    model = YOLO(str(args.model))
    names = {int(i): str(name) for i, name in model.names.items()}
    print_classes(names)
    if args.list:
        return 0

    actions = load_actions()
    dispatcher = None
    if args.execute:
        client = RobotClient(args.robot_url, studio_url=args.studio_url)
        try:
            status = client.verify()
        except Exception as exc:
            print(f"机器人连接失败，未启动动作控制：{exc}", flush=True)
            return 1
        dispatcher = GestureDispatcher(actions, client, args.cooldown)
        print(f"机器人已核验：{status['device_id']} @ {args.robot_url}", flush=True)
    else:
        print("预览模式：只打印识别结果，不向机器人发送动作。加 --execute 才启用动作。", flush=True)
    print("动作映射：手势枪 -> 中弹侧倒；拳头 -> 后退；OK -> 归位；stop -> 停止；比心 -> 爱你-grok版-纠偏；小拇指 -> 你是笨蛋。", flush=True)

    camera = open_camera(cv2, args.camera)
    if not camera.isOpened():
        print(f"无法打开摄像头 {args.camera}。检查 Windows 相机权限，或尝试 --camera 1。", flush=True)
        return 1

    stabilizer = StableGesture(args.stable_frames)
    window_name = "HaGRIDv2 gesture recognition - Q to quit"
    if not args.no_preview:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
    print("开始识别。终端按 Ctrl+C；预览窗口按 Q 或 Esc 退出。", flush=True)
    print("预览与识别已分离：画面持续刷新，识别线程只处理最新帧。", flush=True)
    executor = ThreadPoolExecutor(max_workers=1)
    motion_executor = ThreadPoolExecutor(max_workers=1) if dispatcher else None
    pending = None
    motion_pending = None
    latest_result = None
    try:
        while True:
            if motion_pending is not None and motion_pending.done():
                try:
                    message = motion_pending.result()
                    if message:
                        print(f"[机器人] {message}", flush=True)
                except Exception as exc:
                    print(f"[机器人] 动作发送失败：{exc}", flush=True)
                motion_pending = None
            ok, frame = camera.read()
            if not ok:
                print("摄像头读取失败，识别已停止。", flush=True)
                return 1
            if pending is not None and pending.done():
                latest_result = pending.result()
                pending = None
                gestures, scores = detections(latest_result, names)
                gun_detected, gun_score = detect_finger_gun(
                    latest_result, names, args.gun_conf
                )
                if gun_detected:
                    displayed_gestures = tuple(
                        sorted((set(gestures) - {"point", "like", "three_gun"}) | {"finger_gun"})
                    )
                else:
                    displayed_gestures = gestures
                displayed_scores = {**scores, "finger_gun": gun_score}
                required_frames = confirmation_frames(displayed_gestures, stabilizer.frames)
                if stabilizer.update(displayed_gestures, required_frames):
                    now = datetime.now().strftime("%H:%M:%S")
                    if displayed_gestures:
                        detail = "、".join(
                            f"{ZH.get(name, '手势枪' if name == 'finger_gun' else name)} [{name}] {displayed_scores[name]:.0%}"
                            for name in displayed_gestures
                        )
                        print(f"[{now}] 识别到：{detail}", flush=True)
                    else:
                        print(f"[{now}] 未检测到指定手势", flush=True)
                # Only fresh, consecutively confirmed results may retrigger motion.
                if dispatcher and stabilizer.count >= required_frames and motion_pending is None:
                    motion_pending = motion_executor.submit(dispatcher.dispatch, displayed_gestures)
            if pending is None:
                pending = executor.submit(infer, model, frame.copy(), args.conf, args.imgsz)
            if not args.no_preview:
                preview = latest_result.plot(img=frame.copy()) if latest_result is not None else frame
                if latest_result is not None:
                    preview_gestures, _ = detections(latest_result, names)
                    gun_detected, _ = detect_finger_gun(
                        latest_result, names, args.gun_conf
                    )
                    if gun_detected:
                        preview_gestures = tuple(
                            sorted(
                                (set(preview_gestures) - {"point", "like", "three_gun"})
                                | {"finger_gun"}
                            )
                        )
                    preview = draw_action_labels(cv2, preview, preview_gestures)
                cv2.imshow(window_name, preview)
                if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        if pending is not None:
            pending.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        if motion_executor is not None:
            motion_executor.shutdown(wait=True, cancel_futures=True)
        camera.release()
        if not args.no_preview:
            cv2.destroyAllWindows()
    print("识别已停止。", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
