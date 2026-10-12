# ESP32-S3 固件

本目录运行在机器人主板上，负责执行电脑发送的指令。

- `main/behavior.cpp`：动作编排执行与时序。
- `main/otto_motion.cpp`：四舵机角度和 PWM 输出。
- `main/robot_face.cpp`、`main/board_display.cpp`：表情播放和屏幕驱动。
- `main/audio_input.cpp`、`main/audio_output.cpp`：麦克风和扬声器。
- `main/protocol.cpp`、`main/wifi_http.cpp`、`main/ble_control.cpp`：协议、Wi-Fi 和蓝牙。

可编辑动作库、表情预览和网页界面位于 [web/](../web/)，电脑手势识别位于 [gesture_recognition/](../gesture_recognition/)。

当前为已确认的无摄像头主板，Wi-Fi 和 NimBLE BLE 共用 protocol.cpp。硬件、构建、烧录和验证步骤见项目根目录 README.md。

屏幕逐帧合成，清屏并逆时针旋转 90°。四舵机 GPIO 为 39、17、38、18。

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [assets/](assets/) | storage 分区打包输入；不含完整表情动画分区 |
| [components/](components/) | ESP-IDF 本地组件与兼容层 |
| [main/](main/) | 主控启动、四舵机、屏幕、音频和无线协议 |
| [CMakeLists.txt](CMakeLists.txt) | ESP-IDF 固件工程的顶层构建入口 |
| [README.md](README.md) | ESP32-S3 板端源码、分区和构建配置：使用说明与当前目录文件导航 |
| [dependencies.lock](dependencies.lock) | ESP-IDF 组件版本与校验锁定文件，由组件管理器维护 |
| [partitions.csv](partitions.csv) | Flash 分区布局：程序、存储和表情动画分区等 |
| [sdkconfig.defaults](sdkconfig.defaults) | 固件基础默认构建配置 |
| [sdkconfig.demo](sdkconfig.demo) | 演示固件的完整 ESP-IDF 配置快照 |
| [sdkconfig.emote](sdkconfig.emote) | 表情固件的完整 ESP-IDF 配置快照 |
| [sdkconfig.emote.defaults](sdkconfig.emote.defaults) | 表情播放器编译验证配置，默认禁用舵机输出，需核对候选引脚 |
| [sdkconfig.network-camera.defaults](sdkconfig.network-camera.defaults) | 带摄像头候选主板的联网默认配置，Wi-Fi 使用占位符，需实机核对 |
| [sdkconfig.network-no-camera.defaults](sdkconfig.network-no-camera.defaults) | 无摄像头主板的联网默认配置，Wi-Fi 使用占位符 |
<!-- FILE-INDEX:END -->
