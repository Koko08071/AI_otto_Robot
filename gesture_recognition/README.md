# 摄像头手势识别

在电脑上识别手势，通过 Wi-Fi 或本地 Studio 服务向机器人发送指令。
代码和模型路径均相对于本仓库，不要求存在 D:\Robot。

完整的跨电脑接入说明见[手势识别接入交接文档](../docs/gesture-integration-handoff.md)，包括模型类别、前端视频 API、Wi-Fi/BLE 协议、映射规则和测试顺序。

## 安装与运行

先按[项目首页](../README.md)执行 setup.ps1、下载模型并填写 config.local.json。
从仓库根目录运行：

```powershell
.\.venv\Scripts\python.exe gesture_recognition/recognize.py
.\.venv\Scripts\python.exe gesture_recognition/recognize.py --execute
```

第一条只预览识别；第二条实际控制机器人。网页组合动作还需同时启动 start.ps1。
手势默认用 OpenVINO 模型，可通过 --model 或 OTTO_GESTURE_MODEL 修改。
预览窗口 Q/Esc 或终端 Ctrl+C 退出。

## 文件导航

| 文件 | 用途 |
|---|---|
| recognize.py | 摄像头、推理、类别显示与稳定判定 |
| video_worker.py | 接收浏览器图像并推理 |
| gesture_actions.json | 手势对应的动作或组合 ID |
| motion_bridge.py | 别名、冷却、设备核验和指令发送 |
| robot_config.py | 仓库路径和本地配置 |
| test_*.py | 自动化测试 |

## 当前响应

- 手势枪：中弹侧倒并保持；point 为应用层手势枪判定来源，普通指向可能触发。
- 拳头：后退。
- V 字或反向 V 字：前进。
- OK：返回站姿。
- stop：停止；palm 与 stop_inverted 当前不映射停止。
- 双手比心：播放“爱你-grok版-纠偏”。
- 小拇指、中指及其别名：播放“你是笨蛋”。

同一手势保持时默认每隔 5 秒可重复触发；机器人忙碌时不会叠加动作。
多个冲突手势不会执行，stop 优先。首次实机调试托稳机身。
识别类别总览可用 --list 查看；并非所有识别类别都有机器人响应。
组合声音需要导入个人资源包，详见项目首页。

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [README.md](README.md) | 电脑摄像头识别、手势映射和指令发送：使用说明与当前目录文件导航 |
| [gesture_actions.json](gesture_actions.json) | 手势对应动作与组合 ID：枪形侧倒、拳头后退、V 前进等 |
| [motion_bridge.py](motion_bridge.py) | 手势别名归一化、动作冷却、设备身份核验与 HTTP 指令发送 |
| [recognize.py](recognize.py) | 笔记本摄像头识别入口：YOLO 推理、类别显示、稳定判定及可选机器人响应 |
| [robot_config.py](robot_config.py) | 统一读取本地配置和环境变量，按仓库位置解析模型路径 |
| [test_motion_bridge.py](test_motion_bridge.py) | 手势映射、冷却、停止优先级、设备核验和组合调用测试 |
| [test_recognize.py](test_recognize.py) | 识别稳定判定、手势候选与确认逻辑测试 |
| [test_video_input.py](test_video_input.py) | 网页视频接入与识别流程的手势侧测试 |
| [video_worker.py](video_worker.py) | 网页视频推理子进程：接收图像帧并返回手势识别结果 |
<!-- FILE-INDEX:END -->
