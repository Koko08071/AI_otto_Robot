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

启动步骤见[项目首页](../README.md)。模型和本机音频文件未随仓库上传；新增屏幕表情还需同步机器人固件资源。
