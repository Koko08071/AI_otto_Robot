# 手势模型

已将实际使用的 OpenVINO YOLOv10x 模型上传到本项目 GitHub Releases，包含 34 类手势。

- 完整 Windows 运行包内已包含模型，无需再次下载。
- 源码用户运行 `python tools/download_models.py --kind gesture`，从本项目的发布附件下载并校验。
- 解压位置：`models/YOLOv10x_gestures_openvino_model/`，包含 `.xml`、`.bin` 和 `metadata.yaml`。
- 上游权重来源：[HaGRID](https://github.com/hukenovs/hagrid)，保留并遵守上游模型和数据使用条件。

权重超过 GitHub 普通 Git 单文件 100 MiB 限制，因此以 Releases 附件提供，不使用需要额外配置的 Git LFS。

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [README.md](README.md) | GitHub Releases 手势模型下载说明：使用说明与当前目录文件导航 |
<!-- FILE-INDEX:END -->
