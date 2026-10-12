# 离线语音模型

本项目 GitHub Releases 提供已用于运行的 Faster-Whisper base 模型。

- 完整 Windows 运行包内已包含，无需联网识别。
- 源码用户运行 `python tools/download_models.py --kind voice` 下载并校验。
- 文件位于 `voice-model/base/`：`model.bin`、`config.json`、`tokenizer.json` 和 `vocabulary.txt`。
- 上游：[Systran/faster-whisper-base](https://huggingface.co/Systran/faster-whisper-base)，基于 OpenAI Whisper；许可证与使用条件以对应上游为准。

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [README.md](README.md) | GitHub Releases 离线语音模型下载说明：使用说明与当前目录文件导航 |
<!-- FILE-INDEX:END -->
