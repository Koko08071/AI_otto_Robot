# 安装和迁移工具

在仓库根目录运行，Python 使用 `.venv/Scripts/python.exe`。

| 文件 | 用途 |
|---|---|
| `download_models.py` | 下载手势权重并导出 OpenVINO，下载离线语音模型；可用 `--kind gesture` 或 `--kind voice` 单独选择 |
| `check_environment.py` | 检查 Python 依赖、模型目录和组合引用的声音文件，不连接机器人 |
| `resources.py` | 导出或导入音频及个人动作覆盖 ZIP；拒绝覆盖已有文件 |
| `windows_tts.ps1` | 供声音编排器调用的 Windows 中文语音合成脚本 |

首次安装运行根目录 `setup.ps1`，启动网页运行 `start.ps1`。本地设备配置见 `config.local.json`，详细操作见根目录 README。
