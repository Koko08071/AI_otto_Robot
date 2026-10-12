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
