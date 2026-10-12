# Otto Robot Platform

一个面向少儿编程与互动展示的 Otto 人形机器人项目，包含：

- 四舵机动作控制与动作编排
- ST7789 表情屏资源与表情播放
- Wi-Fi / BLE 网页控制台
- 多轨动作、表情、声音编排器
- 笔记本摄像头 YOLO 手势识别
- 语音监听与关键词触发组合动作
- ESP32-S3 固件源码

## 项目结构

```text
firmware/              ESP32-S3 / ESP-IDF 固件源码
web/                   本地网页控制台、多轨编排器与资源库
gesture_recognition/   摄像头手势识别和手势到动作映射
docs/                  硬件、通信、动作和维护文档
tools/                 构建与校验工具
```

## 快速启动网页控制台

Windows PowerShell：

```powershell
cd web
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OTTO_DEVICE_URL = "http://机器人IP"
\.venv\Scripts\python.exe server.py
```

打开：

- `http://127.0.0.1:8765/`：实时控制台
- `http://127.0.0.1:8765/composer.html`：多轨编排器
- `http://127.0.0.1:8765/emo-preview.html`：表情预览

## 启动手势识别

把模型放在 `models/YOLOv10x_gestures_openvino_model/`，或通过参数指定模型目录：

```powershell
py -m pip install ultralytics opencv-python numpy
py gesture_recognition/recognize.py --model models/YOLOv10x_gestures_openvino_model
py gesture_recognition/recognize.py --model models/YOLOv10x_gestures_openvino_model --execute --robot-url http://机器人IP
```

默认映射见 `gesture_recognition/gesture_actions.json`。修改动作时同步更新该文件和网页资源库中的 `web/static/actions.json`。

## 安全与提交边界

不要把 Wi-Fi 密码、API 密钥、真实设备配置、YOLO 权重、语音模型、编译产物或刷机二进制提交到公开仓库。使用 `.env` 配置设备地址；`.env` 已被 `.gitignore` 忽略。

首次实机运行请托稳机器人，准备断开舵机电源。网页停止按钮不是硬件急停。

## 开发文档

- [硬件与通信说明](docs/hardware-and-protocol.md)
- [动作与手势映射](docs/gesture-actions.md)
- [网页与多轨编排器](docs/web-composer.md)
- [开发与发布清单](docs/maintenance.md)
