# 手势动作映射

当前摄像头识别在笔记本电脑运行，机器人通过 Wi-Fi 接收响应。

| 手势 | 应用层名称 | 响应 |
|---|---|---|
| 手势枪 | `finger_gun` | 中弹侧倒并保持倒地 |
| 拳头 | `fist` | 后退 |
| OK | `ok` | 返回站姿 |
| 张开手掌 / Stop | `stop` | 停止当前动作 |
| 双手比心 | `heart` | 播放“爱你”组合 |
| 小拇指 | `little_finger` | 播放“你是笨蛋”组合 |
| 中指 | `middle_finger` | 播放“你是笨蛋”组合 |

修改映射：编辑 `gesture_recognition/gesture_actions.json`。组合动作通过保存的组合 ID 执行，必须保证网页组合库中仍存在对应 ID。
