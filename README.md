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
```

## 按功能找文件

动作和表情集中在 `web/`，手势识别在 `gesture_recognition/`，机器人板端执行代码在 `firmware/`。点击下面的路径即可进入对应文件。

| 要查看或修改的功能 | 文件位置 | 内容 |
|---|---|---|
| 动作库 | [web/static/actions.json](web/static/actions.json) | 前进、后退、跳舞、中弹侧倒等动作，以及角度、幅度、周期、时长 |
| 表情目录 | [web/static/expressions.json](web/static/expressions.json) | 表情名称、ID、时长和预览资源路径 |
| 表情素材 | [web/static/official/](web/static/official/) / [web/static/concepts/](web/static/concepts/) | 表情图片、GIF 和缩略预览；网页素材不等于已烧录到机器人 |
| 网页前端 | [web/static/](web/static/) | 首页 index.html、交互 app.js、样式 styles.css 等 |
| 多轨编排器 | [web/static/composer.js](web/static/composer.js) | 配套 composer.html / composer.css，编排动作、表情和声音 |
| 已保存组合 | [web/library/compositions/](web/library/compositions/) | “爱你”“你是笨蛋”等组合的轨道、片段和触发词；包含保存时的资源快照 |
| 语音控制 | [web/voice_trigger.py](web/voice_trigger.py) | 语音识别、唤醒词和组合触发逻辑 |
| 手势识别 | [gesture_recognition/recognize.py](gesture_recognition/recognize.py) | 摄像头读取、YOLO 识别、类别显示与稳定判定 |
| 手势对应动作 | [gesture_recognition/gesture_actions.json](gesture_recognition/gesture_actions.json) | 配置识别到某个手势后执行哪个动作或组合 |
| 手势指令发送 | [gesture_recognition/motion_bridge.py](gesture_recognition/motion_bridge.py) | 手势别名、冷却、设备核验及动作发送 |
| 网页摄像头接入 | [web/video_input.py](web/video_input.py) | 将浏览器视频帧接入手势识别流程 |
| 网页服务与通信 | [web/server.py](web/server.py) / [web/ble_link.py](web/ble_link.py) | HTTP 服务、机器人指令转发和蓝牙通信 |
| 板端动作执行 | [firmware/main/behavior.cpp](firmware/main/behavior.cpp) / [firmware/main/otto_motion.cpp](firmware/main/otto_motion.cpp) | 动作时序、插值和舵机 PWM 输出 |
| 板端表情显示 | [firmware/main/robot_face.cpp](firmware/main/robot_face.cpp) / [firmware/main/board_display.cpp](firmware/main/board_display.cpp) | 动画播放和屏幕驱动 |
| 使用与维护文档 | [docs/](docs/) | 硬件通信、手势映射、编排器和维护说明 |

修改动作库后，已保存组合中的动作快照不会自动更新；需要在编排器里更新对应片段并重新保存。

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

## 参考资料

本项目的手势、动作和入门搭建分别参考以下资料。上游项目的名称、图片、代码和许可证仍归原作者所有；本仓库只保存针对当前 ESP32-S3 Otto 机器人的适配代码和配置。

### 1. 手势识别参考：HaGRID

手势类别和视觉样例参考 [HaGRID 手势总览](https://github.com/hukenovs/hagrid/blob/master/images/gestures.png)。当前识别在笔记本电脑摄像头上运行，使用 YOLO 模型检测手势，再通过 `gesture_recognition/gesture_actions.json` 映射为机器人行为。

![HaGRID 手势类别参考](https://raw.githubusercontent.com/hukenovs/hagrid/master/images/gestures.png)

当前项目使用的核心交互映射：

| 识别手势 | 机器人响应 |
|---|---|
| 手势枪 | 中弹侧倒并保持倒地 |
| 拳头 | 后退 |
| OK | 返回站姿 |
| 张开手掌 / Stop | 停止当前动作 |
| 双手比心 | 播放“爱你”组合 |
| 小拇指 / 中指 | 播放“你是笨蛋”组合 |

HaGRID 的 `three_gun` 是数据集定义的三指枪形，不等同于所有食指加拇指的手枪姿势；本项目在应用层对模型结果做了 `finger_gun` 映射，详细逻辑见 `gesture_recognition/recognize.py`。

### 2. 动作参考：OttoDIY Docs

动作名称、基础动作逻辑和 Otto 编程方式参考 [OttoDIY Docs](https://github.com/txp666/ottodiy-docs)。本项目将动作适配为 ESP32-S3 四舵机协议：

- `move`：在指定时间内移动到四轴目标角度
- `oscillate`：按周期和幅度连续摆动
- `hold`：保持当前姿态
- `output`：启用或关闭舵机 PWM

动作资源位于 `web/static/actions.json`，手势专用动作位于 `gesture_recognition/gesture_actions.json`。四轴顺序固定为 `[左腿, 右腿, 左脚, 右脚]`。原始 OttoDIY 动作与本项目补全版动作均应先在无负载、软垫环境下验证。

### 3. 入门复刻教程：OttoDIY Getting Started

硬件安装、舵机连接、Arduino/开发环境和基础动作的入门流程参考 [OttoDIY Getting Started](https://ottodiy.tech/docs/getting-started)。结合本项目复刻时，建议按以下顺序进行：

1. 按 OttoDIY 教程完成机器人结构组装，确认四个舵机机械中位和连杆没有卡滞。
2. 根据 [硬件与通信说明](docs/hardware-and-protocol.md) 核对当前 ESP32-S3 的舵机通道和 GPIO，不直接套用其他 Otto 主控板的引脚定义。
3. 使用 `firmware/` 中的 ESP-IDF 工程编译固件。公开仓库中的 Wi-Fi 配置是占位符，烧录前在本地配置真实 SSID 和密码。
4. 先通过网页控制台发送单轴小幅度姿态，确认左右腿、左右脚映射正确，再测试完整动作。
5. 启动 `web/server.py`，打开网页控制台，选择 Wi-Fi 或 BLE 连接机器人。
6. 启动摄像头手势识别；只观察识别结果时不加 `--execute`，确认类别稳定后再加 `--execute` 控制机器人。
7. 在多轨编排器中组合动作、表情和声音，并保存为可复用的互动程序。

复刻过程中的安全边界：机器人首次动作测试必须托稳机身；动作幅度应从小到大调试；网页“停止”属于软件指令，不等同于硬件急停；不要在公开仓库提交 Wi-Fi 密码、API Token、模型权重或刷机产物。

## 上游链接与许可

- [HaGRID](https://github.com/hukenovs/hagrid)：手势数据集和类别参考，请遵守其许可证与数据使用要求。
- [OttoDIY Docs](https://github.com/txp666/ottodiy-docs)：OttoDIY 文档参考。
- [OttoDIY Getting Started](https://ottodiy.tech/docs/getting-started)：官方入门教程。
- [OttoDIYLib](https://github.com/OttoDIY/OttoDIYLib)：动作算法参考，本项目保留相应许可证说明。
