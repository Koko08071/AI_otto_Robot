# 机器人主控程序

| 文件 | 职责 |
|---|---|
| main.cpp / robot.cpp | 启动、初始化与模块协调 |
| behavior.cpp | 动作时序、插值和组合执行 |
| otto_motion.cpp | 舵机角度与 PWM 输出 |
| robot_face.cpp / board_display.cpp | 表情播放与屏幕驱动 |
| audio_input.cpp / audio_output.cpp | 麦克风采集与扬声器播放 |
| protocol.cpp | 控制指令解析 |
| wifi_http.cpp / ble_control.cpp | Wi-Fi 与蓝牙通信 |
| board_profile.hpp | 硬件引脚与主板配置 |
| Kconfig.projbuild | ESP-IDF 配置选项 |
| CMakeLists.txt | 源文件、依赖及资源分区构建 |

配套 .hpp 为模块接口。修改引脚前请核对实际主板。
