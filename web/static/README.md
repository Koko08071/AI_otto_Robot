# 前端与动作表情资源

| 位置 | 用途 |
|---|---|
| actions.json | 舵机动作、角度、周期与时长 |
| expressions.json | 表情 ID、名称、时长和预览地址 |
| index.html / app.js | 控制台首页和交互逻辑 |
| composer.html / composer.js / composer.css | 多轨编排界面 |
| voice相关交互 | 由页面脚本调用 ../voice_trigger.py 对应服务接口 |
| source_modes.js / camera_labels.js | 输入模式和摄像头识别交互 |
| official/ / concepts/ | 表情预览素材 |
| *.css | 页面样式 |

后端入口在 ../server.py。组合保存在 ../library/compositions/。
