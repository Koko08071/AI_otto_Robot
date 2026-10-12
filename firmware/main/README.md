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

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [CMakeLists.txt](CMakeLists.txt) | 注册主控源文件、声明组件依赖并构建 storage 和动画资源分区 |
| [Kconfig.projbuild](Kconfig.projbuild) | ESP-IDF menuconfig 中的主板、网络、表情与舵机配置项 |
| [README.md](README.md) | 主控启动、四舵机、屏幕、音频和无线协议：使用说明与当前目录文件导航 |
| [audio_input.cpp](audio_input.cpp) | 麦克风音频采集的实现 |
| [audio_input.hpp](audio_input.hpp) | 麦克风音频采集的接口声明 |
| [audio_output.cpp](audio_output.cpp) | 扬声器音频播放的实现 |
| [audio_output.hpp](audio_output.hpp) | 扬声器音频播放的接口声明 |
| [behavior.cpp](behavior.cpp) | 动作程序解析、执行时序与分段调度的实现 |
| [behavior.hpp](behavior.hpp) | 动作程序解析、执行时序与分段调度的接口声明 |
| [behavior_model.hpp](behavior_model.hpp) | 动作帧、分段与组合程序等数据结构及辅助逻辑 |
| [ble_control.cpp](ble_control.cpp) | BLE 广播、连接与控制指令通道的实现 |
| [ble_control.hpp](ble_control.hpp) | BLE 广播、连接与控制指令通道的接口声明 |
| [board_display.cpp](board_display.cpp) | 屏幕初始化、图像绘制与显示方向处理的实现 |
| [board_display.hpp](board_display.hpp) | 屏幕初始化、图像绘制与显示方向处理的接口声明 |
| [board_profile.hpp](board_profile.hpp) | 主板类型和 GPIO 定义，包括舵机与屏幕引脚 |
| [idf_component.yml](idf_component.yml) | 主控组件所需的 ESP-IDF 第三方依赖声明 |
| [main.cpp](main.cpp) | 固件启动入口与主任务的实现 |
| [motion_types.hpp](motion_types.hpp) | 四轴舵机姿态 Pose 的类型定义 |
| [otto_motion.cpp](otto_motion.cpp) | 四舵机 PWM 输出、姿态插值与周期摆动的实现 |
| [otto_motion.hpp](otto_motion.hpp) | 四舵机 PWM 输出、姿态插值与周期摆动的接口声明 |
| [protocol.cpp](protocol.cpp) | 机器人控制协议、指令解析与状态响应的实现 |
| [protocol.hpp](protocol.hpp) | 机器人控制协议、指令解析与状态响应的接口声明 |
| [robot.cpp](robot.cpp) | 机器人模块初始化、状态和整体协调的实现 |
| [robot.hpp](robot.hpp) | 机器人模块初始化、状态和整体协调的接口声明 |
| [robot_face.cpp](robot_face.cpp) | 表情动画选择、播放与循环控制的实现 |
| [robot_face.hpp](robot_face.hpp) | 表情动画选择、播放与循环控制的接口声明 |
| [wifi_http.cpp](wifi_http.cpp) | Wi-Fi 初始化及 HTTP 控制服务的实现 |
| [wifi_http.hpp](wifi_http.hpp) | Wi-Fi 初始化及 HTTP 控制服务的接口声明 |
<!-- FILE-INDEX:END -->
