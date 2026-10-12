# 生图提示词指南（头屏专用）

给父代理 / 生图模型用。每次只出**一张头脸关键帧**。

## 英文提示骨架

```
Square 1:1 robot FACE SCREEN keyframe, head-only close-up filling the frame,
OLED face display style like LivingAI EMO / Espressif Otto eyes,
solid pure black background, no room, no floor, no torso, no arms, no legs, no feet,
cute expressive eyes dominate the frame, clean sticker/cartoon face, high contrast,
[EXPRESSION DETAIL HERE], centered composition, no full-body chibi robot
```

## 负面词（强烈建议）

```
full body, torso, chest, arms, hands holding instruments, legs, feet, shoes,
walking, standing, sitting, room, scene, background furniture, floor,
wide shot, character sheet, multiple characters
```

## 各表情 DETAIL 示例

| id | DETAIL |
|----|--------|
| dog_act | floppy puppy ears on the head, soft dog nose, tongue out, still a robot face screen |
| cat_act | pointed cat ears on top of head, whiskers, cute cat eyes, robot face only |
| music_25s | happy musical eyes, tiny floating notes near the face, NO piano body, NO sitting robot |
| guitar_act | joyful eyes, small floating music notes beside face, NO guitar body, NO arms |
| shot_die | cracked glass over the face panel, X eyes, tongue out, head only |
| bliss_bub | heart eyes, pink bubbles around the head only |
| sob_flood | huge crying eyes, tears spraying, head fill frame |
| steam_mad | angry eyes, steam puffs from temples, head only |

## 输出

- 优先 1024×1024 或 1280×1280 PNG
- 文件名：`<id>_head_01.png`
- 丢进 `web/static/official/_drafts/head_only/`
