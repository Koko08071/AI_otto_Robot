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

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [concepts/](concepts/) | 彩色眼镜、面罩等概念表情预览 |
| [official/](official/) | 表情 GIF、缩略视频与候选素材 |
| [README.md](README.md) | 浏览器页面、样式、交互脚本和动作表情目录：使用说明与当前目录文件导航 |
| [actions.json](actions.json) | 可编辑的四舵机动作库，含角度、幅度、周期、时长和节奏变体 |
| [app.js](app.js) | 控制台交互：连接、状态刷新、动作编辑、舵机姿态与表情播放 |
| [camera_labels.js](camera_labels.js) | 控制台摄像头采集、视频帧上传及识别标签显示 |
| [composer.css](composer.css) | 多轨编排器布局、轨道、片段与属性面板样式 |
| [composer.html](composer.html) | 多轨编排器页面：组合列表、资源库、预览、属性面板及时间轴 |
| [composer.js](composer.js) | 多轨拖放、吸附、片段编辑、预览、保存、撤销及实机组合运行 |
| [concepts.css](concepts.css) | 彩色概念表情预览页面样式 |
| [concepts.json](concepts.json) | 彩色概念表情的名称、ID 和预览目录 |
| [dashboard.css](dashboard.css) | 控制台面板和资源展示的补充样式 |
| [emo-preview.html](emo-preview.html) | 彩色概念表情的独立展示预览页面 |
| [expressions.json](expressions.json) | 表情 ID、中文名称、预览、时长及分段循环元数据目录 |
| [index.html](index.html) | 机器人控制台页面：连接方式、舵机调试、动作和表情库 |
| [source_modes.css](source_modes.css) | 输入来源切换、识别状态和相关控件样式 |
| [source_modes.js](source_modes.js) | 编排器语音/视频输入模式切换、摄像头上传和状态交互 |
| [styles.css](styles.css) | 控制台基础布局、颜色、按钮和组件样式 |
<!-- FILE-INDEX:END -->
