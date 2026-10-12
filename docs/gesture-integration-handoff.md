# 手势识别接入交接文档

本文用于把“笔记本摄像头识别手势，机器人执行动作、表情或声音组合”接入另一台电脑或另一个 AI。本文只描述当前已经实现的能力；动作模仿、IMU 被拿起反应、桌边防跌落属于后续构想，不是当前接口。

## 1. 系统数据流

```text
笔记本摄像头
  -> YOLOv10x_gestures OpenVINO 模型
  -> 检测类别、置信度和手部框
  -> 应用层归一化与连续帧确认
  -> gesture_actions.json 手势映射
  -> Wi-Fi HTTP 或本地 Studio BLE 链路
  -> Otto 执行动作、表情或多轨组合
```

- 推理在笔记本电脑上进行，机器人不运行 YOLO 模型。
- 机器人只接收已经确定的动作、表情或组合指令。
- 独立命令行模式直接调用机器人 HTTP；前端模式由 `web/server.py` 负责识别进程和 BLE/Wi-Fi 链路。
- 机器人必须独立供电；USB 主要用于刷机和诊断，不是无线控制的必要连接。
- 当前实现默认核验设备 ID，避免误控制其他机器人。

## 2. 关键文件

| 路径 | 职责 |
|---|---|
| `gesture_recognition/recognize.py` | 独立摄像头入口、模型推理、终端输出、稳定判定和可选执行 |
| `gesture_recognition/video_worker.py` | 前端识别子进程；stdin 收 JPEG，stdout 返回 JSON，不直接控制机器人 |
| `gesture_recognition/motion_bridge.py` | 设备核验、动作/组合发送、冷却和冲突处理 |
| `gesture_recognition/gesture_actions.json` | 手势到程序或组合的配置 |
| `gesture_recognition/robot_config.py` | 读取本地配置、环境变量和模型路径 |
| `web/video_input.py` | 前端视频会话、稳定帧确认和识别结果转动作 |
| `web/static/camera_labels.js` | 浏览器取帧并调用 `/api/video/*` |
| `web/server.py` | 本地 HTTP 服务、机器人连接、动作/表情/组合接口 |
| `web/ble_link.py` | BLE 扫描和 Nordic UART Service 转发 |
| `models/` | 手势模型说明；完整权重在 Release 或完整 Windows 包中 |
| `web/library/compositions/` | 手势触发的多轨动作、表情、音频组合 JSON |

## 3. 环境和配置

推荐直接下载 Release 的 `Otto-Robot-Windows-v2026.10.12.zip`，完整解压后双击 `START.bat`。它已经包含 Python、依赖、模型、音频和前端。

源码方式在仓库根目录运行：

```powershell
.\setup.ps1
.\.venv\Scripts\python.exe tools\download_models.py --kind all
```

模型默认路径：`models/YOLOv10x_gestures_openvino_model/`，包含 XML、BIN 和 metadata。关键依赖为 `ultralytics`、`openvino`、`opencv-python`、`numpy`、`Pillow`、`bleak`。

复制 `config.example.json` 为 `config.local.json`，填写实际连接信息：

```json
{
  "OTTO_DEVICE_URL": "http://192.168.1.100",
  "OTTO_DEVICE_ID": "14c19f300e70",
  "OTTO_BLE_NAME": "Otto-0E70",
  "OTTO_GESTURE_MODEL": "models/YOLOv10x_gestures_openvino_model",
  "OTTO_PORT": 8765
}
```

`OTTO_DEVICE_URL` 是机器人 IP，不是电脑 IP；`OTTO_DEVICE_ID` 必须和 `/api/status` 返回值一致；`OTTO_BLE_NAME` 是 BLE 广播名。真实 Wi-Fi 密码、API Token 和私人配置不得提交到 GitHub。

## 4. 独立命令行模式

先只识别、不控制机器人：

```powershell
.\.venv\Scripts\python.exe gesture_recognition\recognize.py --list
.\.venv\Scripts\python.exe gesture_recognition\recognize.py --no-preview
```

确认识别稳定后，才启用机器人控制：

```powershell
.\.venv\Scripts\python.exe gesture_recognition\recognize.py --execute
```

常用参数：

| 参数 | 默认值 | 作用 |
|---|---:|---|
| `--camera` | `0` | 摄像头编号，可试 `1` |
| `--conf` | `0.45` | 最低检测置信度 |
| `--gun-conf` | `0.65` | `point` 转手势枪的最低置信度 |
| `--imgsz` | `960` | 推理尺寸，越大通常越准但越慢 |
| `--stable-frames` | `3` | 连续确认帧数 |
| `--cooldown` | `5.0` | 同一持续手势再次触发的间隔秒数 |
| `--robot-url` | 配置值 | 覆盖机器人 Wi-Fi 地址 |
| `--studio-url` | 本地 8765 | 组合服务地址 |
| `--no-preview` | 关闭 | 只输出终端，不打开预览窗 |

预览窗口按 `Q`/`Esc` 退出，终端按 `Ctrl+C`。软件停止不是硬件急停，测试时应准备断开舵机电源。

## 5. 当前模型类别

启动时以 `model.names` 为准打印类别。当前模型包含：

```text
grabbing, grip, holy, point, call, three3, timeout, xsign,
hand_heart, hand_heart2, little_finger, pinkie, middle_finger,
take_picture, dislike, fist, four, like, mute, ok, one, palm,
peace, peace_inverted, rock, stop, stop_inverted, three, three2,
two_up, two_up_inverted, three_gun, thumb_index, thumb_index2,
no_gesture
```

`no_gesture` 不参与动作触发。模型类别数量和名称始终应以运行时 `model.names` 为准。

### 手势枪的特殊规则

当前应用层把模型的 `point` 类在置信度达到 `--gun-conf` 时映射成 `finger_gun`：

```text
point >= gun_conf -> finger_gun -> 中弹侧倒
```

因此普通“指向”也可能触发手势枪动作。模型中的 `three_gun` 是数据集定义的三指枪形，不等同于所有食指加拇指的手枪姿势。要严格区分，需要更换/训练模型或增加几何规则。

## 6. 手势映射

配置文件是 `gesture_recognition/gesture_actions.json`：

| 输入类别/别名 | 归一化名称 | 当前响应 |
|---|---|---|
| `point`（达到 gun-conf） | `finger_gun` | `shot_fall_side` 中弹侧倒并保持 |
| `fist` | `fist` | `walk_reverse_complete_p450` 后退 |
| `peace`, `peace_inverted` | `forward` | `walk_complete_p500` 前进 |
| `ok` | `ok` | `return_home` 返回站姿 |
| `stop` | `stop` | 停止当前动作 |
| `hand_heart`, `hand_heart2` | `heart` | `爱你-grok版-纠偏` 组合 |
| `little_finger`, `pinkie`, `middle_finger`, `mid.finger`, `mid_finger` | `little_finger` | `你是笨蛋` 组合 |

执行规则：

1. 一帧内多个可执行手势同时出现时不执行，避免冲突。
2. `stop` 优先于其他手势。
3. 连续稳定确认后才触发，默认 3 帧。
4. 同一保持手势默认 5 秒后才能再次触发。
5. 失败或机器人忙碌时有约 2 秒重试窗口，不会每帧重复发送。
6. 组合必须存在于 `web/library/compositions/`，且 ID 和名称都匹配。
7. `palm`、`stop_inverted` 当前没有停止映射。

## 7. 前端视频接口

启动服务：

```powershell
.\.venv\Scripts\python.exe tools\portable_launcher.py
```

浏览器前端流程：

1. `POST /api/video/start` 获取 token。
2. 浏览器把 JPEG 二进制帧发到 `POST /api/video/frame`。
3. 请求头为 `X-Video-Token: <token>`。
4. 响应包含 `labels`、`names`、`active` 和可选 `message`。
5. 结束时 `POST /api/video/stop`，body 为 `{ "token": "..." }`。

帧约束：`image/jpeg`，最大 1.5 MB，输入最大边不能超过 1920 像素；视频会话约 15 秒没有新帧会失效。`/api/video/preview` 只测试模型，不需要 token，也不会控制机器人。

典型响应：

```json
{
  "labels": ["fist"],
  "names": ["拳头"],
  "message": "fist -> 后退（已发送）",
  "active": true
}
```

## 8. 机器人通信接口

常用机器人 HTTP 接口：

```text
GET  /api/status
POST /api/play
POST /api/stop
POST /api/home
POST /api/face
POST /api/output
```

动作 `pose` 顺序固定为 `[左腿, 右腿, 左脚, 右脚]`，GPIO 对应 `[39, 17, 38, 18]`，角度范围协议上为 `0-180`，实际应遵守已校准的机械安全范围。

Wi-Fi 模式由 `RobotClient` 直接向机器人 URL 发 HTTP；BLE 模式由 `web/ble_link.py` 扫描并桥接。BLE 使用 Nordic UART Service：

```text
Service  6e400001-b5a3-f393-e0a9-e50e24dcca9e
RX 写入  6e400002-b5a3-f393-e0a9-e50e24dcca9e
TX 读取  6e400003-b5a3-f393-e0a9-e50e24dcca9e
```

BLE JSON 帧格式：`{"id":1,"path":"/api/play","body":{}}\n`；单请求最大 65536 字节，代码按 180 字节分片写入。浏览器不直接连 BLE，而是由本地 Python 服务桥接。

## 9. 另一个 AI 的接入顺序

1. 阅读本文、`gesture_recognition/README.md`、`docs/gesture-actions.md` 和 `docs/hardware-and-protocol.md`。
2. 运行 `recognize.py --list`，确认模型路径和类别。
3. 不带 `--execute` 运行预览，确认摄像头和类别稳定。
4. 调用 `/api/status`，确认设备 ID 与本地配置一致。
5. 先测试 `ok`、`stop` 和返回站姿，再测试移动。
6. 最后在软垫、托稳机器人条件下测试中弹侧倒。
7. 修改映射只编辑 `gesture_actions.json`；新增组合时同步新增组合 JSON。
8. 替换模型时，先对照 `model.names` 更新类别映射，再调整 `detect_finger_gun` 和阈值。

## 10. 测试和排障

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s gesture_recognition -p "test_*.py"
.\.venv\Scripts\python.exe -m unittest discover -s web/tests -p "test_video_input.py"
.\.venv\Scripts\python.exe tools\check_environment.py
```

| 现象 | 排查 |
|---|---|
| 模型找不到 | 下载模型并确认 `OTTO_GESTURE_MODEL` 指向目录 |
| 画面卡顿 | 降低 `--imgsz` 到 640；大模型更准但 CPU 推理更慢 |
| 识别有输出但不动 | 必须加 `--execute`；检查设备核验、busy 状态和映射配置 |
| 手势枪误触发 | 当前 `point` 会映射为 `finger_gun`；提高 `--gun-conf` 或修改专用判定 |
| 组合无响应 | 启动 Studio，检查组合 ID、名称和音频资源 |
| BLE 扫描不到 | 开启蓝牙、机器人独立供电、确认广播名和单一连接 |
| Wi-Fi 失败 | 确认机器人 IP 可达，不要填电脑 IP，并检查局域网设备隔离 |

## 11. 安全边界

首次执行 `--execute` 前必须先预览。手势枪、拳头和 V 手势会触发动作或移动，测试时托稳机器人并远离桌边。`stop` 是软件指令，不等于物理急停；不要在日志或 GitHub 中暴露私人设备信息。
