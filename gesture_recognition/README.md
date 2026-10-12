# 笔记本实时手势识别

## 文件导航

- `recognize.py`：摄像头采集、模型推理与识别结果显示。
- `gesture_actions.json`：手势对应的动作或组合配置。
- `motion_bridge.py`：手势别名、触发间隔和机器人通信。
- `video_worker.py`：网页视频识别工作进程。
- `test_*.py`：识别和控制逻辑测试。

机器人动作库、表情和语音控制在 [web/](../web/)，本目录负责手势识别及触发。

## 网页视频输入

在 http://127.0.0.1:8765/composer.html 选择“网页麦克风”“视频”或“网页麦克风和视频”，
点击“开启识别”。浏览器会请求所选设备权限。视频来自当前浏览器摄像头，
本机 video_worker.py 使用现有 YOLO 环境推理，网页左上角只显示绿色中文动作名。
网页模式无需另外运行 recognize.py，也不会弹出 OpenCV 窗口。
首页“电脑摄像头”开启后同样会识别并执行手势动作，画面左上角显示绿色中文名称；
关闭摄像头会结束识别会话，页面下方显示最近一次动作发送或跳过的状态。
动作沿用 gesture_actions.json；连续三次确认、同手势五秒间隔、切换手势无额外间隔。
语音组合和视频动作共用忙碌检查，STOP 手势取消组合；网页“停止”同时关闭输入并停止机器人。
切换输入、关闭视频、权限失败或离开页面会释放摄像头；关闭会话后的推理结果不再触发动作。

网页补丁及测试材料位于 D:\Robot\studio_video_patch；实际运行的 Studio 源码在桌面
otto-all-materials-20261010-completed/outputs/otto-wireless-demo/web。
video_input.py 默认读取 D:\Robot\gesture_recognition（可用 OTTO_GESTURE_DIR 指定）。
迁移机器时仍需同时交接 Studio、组合和音频资源，以及模型和 Python 环境。

使用 HaGRIDv2 官方已训练的 YOLOv10x 高精度手势检测模型。识别在笔记本运行，
默认只打印识别结果；加 --execute 后通过 Wi-Fi 控制已核验的 Otto 机器人。
不会刷写固件，不需要 USB。

默认模型位置：D:\Robot\gesture-yolo\models\YOLOv10x_gestures_openvino_model
轻量模型仍保留在 D:\Robot\gesture-yolo\models\YOLOv10n_gestures.pt。

在 VS Code 终端运行：

    D:\Robot\gesture-yolo\Scripts\python.exe .\gesture_recognition\recognize.py

程序启动会打印模型实际包含的全部类别。连续 3 次推理结果一致后，终端打印中文名称、
原始类别和置信度。预览和识别在不同线程运行，识别较慢时会丢弃旧帧，避免视频越积越卡。
预览窗口按 Q/Esc，终端按 Ctrl+C 停止。

## 手势控制机器人

小拇指（little_finger，兼容 pinkie）和中指（middle_finger，兼容 mid.finger）触发 Studio 保存的“你是笨蛋”，
组合 ID a02b547d-0df4-4a68-afdc-a92351ef40fa，当前版本 11、8 片段、10.35 秒；开头归位为原速补全。
与比心共用下面的 Studio 服务及停止逻辑，组合运行中不会重复启动。

比心（hand_heart / hand_heart2）触发 Studio 中已保存的“爱你-grok版-纠偏”，
组合 ID a1cd58a0-74a2-4b2d-a92a-a5cd90637dfc，当前为 33 片段、20.681 秒；开头及结尾归位均为原速。
需运行 http://127.0.0.1:8765 的网页服务并连接同一机器人；可通过 --studio-url 改地址。
使用网页原有组合执行器，包含动作、表情和音频；STOP 会取消组合调度并停止动作。
组合未结束时不会重启或叠加其他动作。同手势 5 秒规则仍适用，但不会打断约 20 秒的组合。
交接还需提供 Studio 服务及其组合、音频等资源；仅复制识别目录无法独立播放此组合。

先确认笔记本与机器人位于可互通的局域网、机器人独立供电，并托稳机器人。
在 VS Code 的 D:\Robot 工作区运行任务 Gesture: Control Otto over Wi-Fi，或执行：

    D:\Robot\gesture-yolo\Scripts\python.exe D:\Robot\gesture_recognition\recognize.py --execute

启动时先通过 /api/status 核验设备 ID 14:c1:9f:30:0e:70；不匹配立即退出。
每次发送前再次核验身份及空闲状态。后退使用同事交接包的中速补全程序，
中弹倒地是基于本机四舵机站姿新编排的受控动作，
保存于 gesture_actions.json：

- 画面显示“手势枪” (finger_gun，当前由 point 类映射) -> 中弹侧倒 shot_fall_side，约 0.78 秒，不自动起身。
- 拳头 (fist) -> 后退 walk_reverse_complete_p450，约 3.29 秒（末段原速归位）。
- 停止手势 (stop) -> 停止当前动作。
- OK (ok) -> 原速约 1.2 秒平滑归位到 [90, 90, 100, 90]；拳头后退的末段归位也使用原速，沿用冷却和忙碌检查。

中弹动作先侧移重心，再继续压低一侧支撑，末段保持 [145, 45, 20, 20]，执行完仍保持舵机输出，
不会自动回到站姿。四舵机无法保证机身安全横倒或控制触地过程；是否真正触地取决于
机身重心、地面和舵机安装。屏幕 shot_die 表情尚未确认已烧录，
因此这段动作目前不自动切换屏幕表情。

手势需连续识别 3 次才能触发，每次动作程序只运行一遍。同一手势持续保持时，
默认从上次发送起至少间隔 5 秒，收到新的稳定识别结果后再执行一次。
切换为其他稳定手势不受此间隔限制；稳定识别到无手势后再次比出也视为新一轮。
机器人忙碌时不叠加动作，当前手势仍保持时隔 2 秒重试；不缓存旧手势。
移开手或识别不稳定时不会自动重复。可用 --cooldown 调整同手势重复间隔。
stop 停止不受间隔限制，持续保持该手势只发送一次停止指令。
同时识别到手势枪和拳头时不执行，防止歧义。终端会输出识别结果及发送成功/失败。
可用 --robot-url http://<实际机器人IP> 指定地址，默认 10.240.103.49。

注意：当前“手势枪”是把模型 point 类作为应用层触发条件，普通指向动作也可能
触发中弹动作。这组侧倒角度尚未做实物运动校验；首次运行请在软垫上托稳机器人，
留出倒向一侧的空间，保护屏幕并准备断开舵机电源。stop 的软件停止只保持当前角度，
不会扶正；网络断开时可能无效，也不是急停。需要扶正时先手动托稳机身，再使用网页“归位”。

只在终端运行：

    D:\Robot\gesture-yolo\Scripts\python.exe .\gesture_recognition\recognize.py --no-preview

只查看类别：加 --list。误识别较多时：--conf 0.6 --stable-frames 5。
摄像头打不开时尝试 --camera 1。

注意：three_gun 是 HaGRID 定义的三指枪形，不保证普通食指和拇指组成的手势枪也能识别。
当前控制映射使用应用层 finger_gun，不直接使用数据集 three_gun 类别。
