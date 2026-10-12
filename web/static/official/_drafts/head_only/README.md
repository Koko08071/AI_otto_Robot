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

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [PROMPT_GUIDE.md](PROMPT_GUIDE.md) | 生图提示词指南（头屏专用）：文档说明 |
| [README.md](README.md) | 头屏关键帧、过渡帧与视觉检查图：使用说明与当前目录文件导航 |
| [_pending_ids.json](_pending_ids.json) | 候选表情的隔离/待确认 ID 清单，不代表已烧录到机身 |
| [_qa_seed_strip.png](_qa_seed_strip.png) | 关键帧候选素材拼图，供视觉检查与对照 |
| [awkward_xx_head_01.jpg](awkward_xx_head_01.jpg) | “尴尬尬笑”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [bird_act_head_01.jpg](bird_act_head_01.jpg) | “变小鸟”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [bliss_bub_head_01.png](bliss_bub_head_01.png) | “幸福泡泡”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [burp_xx_head_01.jpg](burp_xx_head_01.jpg) | “打嗝”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [cat_act_head_01.png](cat_act_head_01.png) | “变小猫”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [cat_act_loop_01.png](cat_act_loop_01.png) | “变小猫”循环关键帧，用于表情制作，不是可直接烧录的动画包 |
| [charge_xx_head_01.jpg](charge_xx_head_01.jpg) | “充电回血”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [dog_act_head_01.jpg](dog_act_head_01.jpg) | “变小狗”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [dog_act_loop_01.png](dog_act_loop_01.png) | “变小狗”循环关键帧，用于表情制作，不是可直接烧录的动画包 |
| [drums_act_head_01.jpg](drums_act_head_01.jpg) | “打鼓”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [glasses_xx_head_01.jpg](glasses_xx_head_01.jpg) | “眼镜反光”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [guitar_act_head_01.jpg](guitar_act_head_01.jpg) | “弹吉他”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [heart_hands_head_01.jpg](heart_hands_head_01.jpg) | “比心”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [hello_wave_head_01.jpg](hello_wave_head_01.jpg) | “招手你好”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [idea_bulb_head_01.jpg](idea_bulb_head_01.jpg) | “灵感灯泡”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [kiss_act_head_01.jpg](kiss_act_head_01.jpg) | “飞吻”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [lightning_xx_head_01.jpg](lightning_xx_head_01.jpg) | “被雷劈”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [magic_act_head_01.jpg](magic_act_head_01.jpg) | “变魔术”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [music_25s_head_01.jpg](music_25s_head_01.jpg) | “弹钢琴”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [nap_zzz_head_01.jpg](nap_zzz_head_01.jpg) | “打瞌睡”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [no_shake_head_01.jpg](no_shake_head_01.jpg) | “摇头拒绝”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [panda_act_head_01.jpg](panda_act_head_01.jpg) | “变熊猫”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [party_xx_head_01.jpg](party_xx_head_01.jpg) | “中彩票撒花”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [qa_shot_f0_smile.png](qa_shot_f0_smile.png) | 中弹表情视觉检查帧：f0_smile（帧号或阶段标记） |
| [qa_shot_f14_loop.png](qa_shot_f14_loop.png) | 中弹表情视觉检查帧：f14_loop（帧号或阶段标记） |
| [qa_shot_f22_outro.png](qa_shot_f22_outro.png) | 中弹表情视觉检查帧：f22_outro（帧号或阶段标记） |
| [qa_shot_f4_flash.png](qa_shot_f4_flash.png) | 中弹表情视觉检查帧：f4_flash（帧号或阶段标记） |
| [qa_shot_f7_crack.png](qa_shot_f7_crack.png) | 中弹表情视觉检查帧：f7_crack（帧号或阶段标记） |
| [qa_shot_f_last.png](qa_shot_f_last.png) | 中弹表情视觉检查帧：f_last（帧号或阶段标记） |
| [rabbit_act_head_01.jpg](rabbit_act_head_01.jpg) | “变兔子”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [rain_sad_head_01.jpg](rain_sad_head_01.jpg) | “下雨撑伞”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [shot_die_f1_smile.jpg](shot_die_f1_smile.jpg) | 中弹表情分镜：微笑起始帧 |
| [shot_die_f2_hit.jpg](shot_die_f2_hit.jpg) | 中弹表情分镜：命中反应帧 |
| [shot_die_f3_crack.jpg](shot_die_f3_crack.jpg) | 中弹表情分镜：裂纹过渡帧 |
| [shot_die_f4_xx.jpg](shot_die_f4_xx.jpg) | 中弹表情分镜：叉眼结束帧 |
| [shot_die_head_01.png](shot_die_head_01.png) | “中弹碎裂”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [shot_die_intro_00.png](shot_die_intro_00.png) | “中弹碎裂”入场过渡帧，用于表情制作，不是可直接烧录的动画包 |
| [shot_die_intro_01.png](shot_die_intro_01.png) | “中弹碎裂”入场过渡帧，用于表情制作，不是可直接烧录的动画包 |
| [shot_die_intro_02.png](shot_die_intro_02.png) | “中弹碎裂”入场过渡帧，用于表情制作，不是可直接烧录的动画包 |
| [shot_die_loop_01.png](shot_die_loop_01.png) | “中弹碎裂”循环关键帧，用于表情制作，不是可直接烧录的动画包 |
| [smile_default_head.png](smile_default_head.png) | “默认微笑”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [smile_default_head_01.png](smile_default_head_01.png) | “默认微笑”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [smug_xx_head_01.jpg](smug_xx_head_01.jpg) | “得意挑眉”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [sneeze_xx_head_01.jpg](sneeze_xx_head_01.jpg) | “打喷嚏”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [sob_flood_head_01.jpg](sob_flood_head_01.jpg) | “泪水喷涌”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [sob_flood_loop_01.png](sob_flood_loop_01.png) | “泪水喷涌”循环关键帧，用于表情制作，不是可直接烧录的动画包 |
| [soul_out_head_01.jpg](soul_out_head_01.jpg) | “灵魂出窍”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [steam_mad_head_01.jpg](steam_mad_head_01.jpg) | “冒蒸汽怒”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [sulk_act_head_01.jpg](sulk_act_head_01.jpg) | “超级委屈”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [trumpet_act_head_01.jpg](trumpet_act_head_01.jpg) | “吹喇叭”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [wink_xx_head_01.jpg](wink_xx_head_01.jpg) | “眨眼挑逗”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [yes_bounce_head_01.jpg](yes_bounce_head_01.jpg) | “大力点头”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [目录说明.md](%E7%9B%AE%E5%BD%95%E8%AF%B4%E6%98%8E.md) | 头屏设计草稿：文档说明 |
<!-- FILE-INDEX:END -->
