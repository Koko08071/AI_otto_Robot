# 安装和迁移工具

在仓库根目录运行，Python 使用 `.venv/Scripts/python.exe`。

| 文件 | 用途 |
|---|---|
| `download_models.py` | 下载手势权重并导出 OpenVINO，下载离线语音模型；可用 `--kind gesture` 或 `--kind voice` 单独选择 |
| `check_environment.py` | 检查 Python 依赖、模型目录和组合引用的声音文件，不连接机器人 |
| `resources.py` | 导出或导入音频及个人动作覆盖 ZIP；拒绝覆盖已有文件 |
| `windows_tts.ps1` | 供声音编排器调用的 Windows 中文语音合成脚本 |
| `portable_launcher.py` | 便携包启动器，自动选择空闲端口并打开浏览器；`--smoke` 只检查启动，不连接机器人 |
| `build_handoff.py` | 在配置好的 Windows 虚拟环境中打包源代码、模型、素材和独立 Python 运行时；使用方法见 `--help` |

首次安装运行根目录 `setup.ps1`，启动网页运行 `start.ps1`。本地设备配置见 `config.local.json`，详细操作见根目录 README。

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [README.md](README.md) | 模型下载、资源迁移、环境检查和便携包工具：使用说明与当前目录文件导航 |
| [build_handoff.py](build_handoff.py) | 收集源码、模型、素材及 Python 运行库，生成 Windows 同事交接 ZIP |
| [check_environment.py](check_environment.py) | 检查 Python 依赖、模型目录及组合引用的音频，不发送机器人动作 |
| [download_models.py](download_models.py) | 下载 HaGRID 手势权重并导出 OpenVINO，同时支持下载离线语音模型 |
| [portable_launcher.py](portable_launcher.py) | 便携包启动器：选择空闲端口、启动服务、打开浏览器；支持无动作启动检查 |
| [resources.py](resources.py) | 导入或导出声音和个人动作覆盖 ZIP，拒绝覆盖已有文件 |
| [update_file_index.py](update_file_index.py) | 维护中文文件索引，按配置说明及组合、表情元数据生成各级 README 导航 |
| [windows_tts.ps1](windows_tts.ps1) | 调用 Windows System.Speech 将中文文本合成为 WAV |
<!-- FILE-INDEX:END -->
