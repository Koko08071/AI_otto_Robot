# 头屏关键帧收件箱（HEAD-ONLY · 三段式）

机身屏幕只显示**头部/脸**。动画必须是 **Entrance → Loop → Return**（对齐
`esp_emote_gen_player` / 《表情动效系统规范》），禁止单张图左右晃动。

## 投放命名

| 文件 | 作用 |
|------|------|
| `smile_default_head.png` | 所有表情 Intro 起点 / Outro 终点 |
| `<id>_loop_01.png`（可 `_02`…） | Loop 高潮脸；多张会在 Loop 内插值 |
| `<id>_intro_01.png` | 可选过渡脸（如裂纹半开、耳朵刚长出） |
| `<id>_head_01.png` | 兼容旧名 = loop 峰 |

## 构图

纯黑底、头脸填满、无躯干腿脚。才艺类只做脸上反应 + 贴近脸的小符号。

## 生成

```bash
.venv-expr/bin/python tools/build_segmented_emotes.py --list
.venv-expr/bin/python tools/build_segmented_emotes.py shot_die bliss_bub --eaf
```

旧的 `build_head_only_emotes.py` 仅作兼容（单帧晃动），**新表情请用 segmented**。

打包 / 烧录步骤见 `docs/emote_packing_esp_emote_gen_player.md`。默认不刷机。
