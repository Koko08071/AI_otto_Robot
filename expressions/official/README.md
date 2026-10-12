# 表情分区镜像

`all_emote_assets.bin` 包含交接包中的官方精简表情与 32 个头屏表情，写入地址为 `0x800000`。分区预留 8 MB，要求匹配本项目 16 MB Flash 分区表。与网页表情目录交叉核对后使用，目录中的全部预览不一定都在该镜像中。

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [README.md](README.md) | 官方精简与头屏表情分区镜像：使用说明与当前目录文件导航 |
| [all_emote_assets.bin](all_emote_assets.bin) | 固件 CMake 构建引用的动画分区输入，与 flash 中同名镜像一致 |
<!-- FILE-INDEX:END -->
