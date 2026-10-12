# 网页、动作、表情与语音控制

| 位置 | 用途 |
|---|---|
| [static/actions.json](static/actions.json) | 动作库：角度、幅度、周期和时长 |
| [static/expressions.json](static/expressions.json) | 表情目录和资源 ID |
| [static/official/](static/official/) / [static/concepts/](static/concepts/) | 表情预览素材 |
| [static/index.html](static/index.html) / [static/app.js](static/app.js) | 控制台首页与交互 |
| [static/composer.html](static/composer.html) / [static/composer.js](static/composer.js) | 多轨编排界面 |
| [library/compositions/](library/compositions/) | 已保存的动作、表情、声音组合 |
| [voice_trigger.py](voice_trigger.py) | 语音识别与唤醒触发 |
| [video_input.py](video_input.py) | 网页摄像头接入手势识别 |
| [server.py](server.py) / [ble_link.py](ble_link.py) | 网页服务、Wi-Fi 与蓝牙通信 |

启动步骤见[项目首页](../README.md)。现有音频随源码提供，模型和完整 Windows 环境通过本项目 Releases 提供；新增屏幕表情仍需同步机器人固件资源。

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [library/](library/) | 已保存组合以及本地声音资源 |
| [static/](static/) | 浏览器页面、样式、交互脚本和动作表情目录 |
| [tests/](tests/) | 网页交互、协议、资源管理和识别接入测试 |
| [README.md](README.md) | 网页服务、多轨组合、语音识别和机器人通信：使用说明与当前目录文件导航 |
| [audio_tools.py](audio_tools.py) | 查找系统 FFmpeg，或回退到 Python 依赖内置的 FFmpeg |
| [ble_link.py](ble_link.py) | BLE 扫描、连接、指令收发与断线恢复 |
| [composer_store.py](composer_store.py) | 管理组合与音频的保存、校验、上传、合成、资源快照和触发词匹配 |
| [requirements.txt](requirements.txt) | 网页后端的基础 Python 依赖，根目录依赖清单会引用此文件 |
| [server.py](server.py) | 本地 HTTP 服务入口，提供控制接口、资源目录及组合执行调度 |
| [video_input.py](video_input.py) | 管理浏览器视频帧和识别子进程，将识别结果接入动作与组合调度 |
| [voice_trigger.py](voice_trigger.py) | 离线语音转写、唤醒词与关键词监听，触发对应组合 |
<!-- FILE-INDEX:END -->
