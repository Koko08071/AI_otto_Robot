# 全部目录与文件用途索引

本索引覆盖 371 个源码、配置、文档与素材文件，按 28 个目录分组。每级 README 也列出直属文件和子目录。

GitHub 文件列表中间一列是最近一次提交说明，并非固定备注；后续修改会更新它。固定用途说明请查看本索引或所在目录 README。组合名和表情名来自项目实际 JSON 元数据。模型与运行环境通过 GitHub Releases 提供；音频及公开刷机文件随源码提供，密码配置不公开。

维护时运行 `python tools/update_file_index.py` 更新索引；新增代码文件需先在脚本中补充用途，新增素材需补充对应资源目录元数据。

## 仓库根目录

项目入口、配置、安装启动与同事交接

| 文件 | 用途说明 |
|---|---|
| [.gitignore](../.gitignore) | 忽略本地配置、模型、虚拟环境、音频、压缩包与构建产物，避免误提交 |
| [CHECK.bat](../CHECK.bat) | 便携交接包双击检查入口，报告缺少的依赖、模型或声音文件 |
| [HANDOFF.md](../HANDOFF.md) | 同事交接详解：启动、Wi-Fi/BLE 连接、前端演示、故障排查与保存位置 |
| [QUICKSTART.html](../QUICKSTART.html) | 无需编辑器即可在浏览器打开的同事图文快速指南 |
| [README.md](../README.md) | 项目入口、配置、安装启动与同事交接：使用说明与当前目录文件导航 |
| [START.bat](../START.bat) | 便携交接包双击启动入口，使用 runtime 内的 Python 并自动打开浏览器 |
| [config.example.json](../config.example.json) | 机器人 IP、设备 ID、蓝牙名、模型路径和网页端口的配置模板；复制为 config.local.json 后本地填写 |
| [release-assets.json](../release-assets.json) | GitHub 发布附件名称、下载链接和 SHA256 校验清单 |
| [requirements.txt](../requirements.txt) | 电脑端总依赖清单，包含网页服务、手势推理和音频处理 |
| [setup.ps1](../setup.ps1) | 创建仓库内 .venv、安装 Python 依赖并生成本地配置 |
| [start.ps1](../start.ps1) | 使用 .venv 启动网页服务，适用于源码安装方式 |

## docs

硬件通信、功能说明、维护文档和展示素材

| 文件 | 用途说明 |
|---|---|
| [README.md](../docs/README.md) | 硬件通信、功能说明、维护文档和展示素材：使用说明与当前目录文件导航 |
| [file-index.md](../docs/file-index.md) | 全仓库逐目录、逐文件的中文用途总索引 |
| [gesture-actions.md](../docs/gesture-actions.md) | 手势动作映射：文档说明 |
| [gesture-integration-handoff.md](../docs/gesture-integration-handoff.md) | 手势识别接入交接文档：文档说明 |
| [hardware-and-protocol.md](../docs/hardware-and-protocol.md) | 硬件与通信：文档说明 |
| [maintenance.md](../docs/maintenance.md) | 维护与发布：文档说明 |
| [web-composer.md](../docs/web-composer.md) | 网页与多轨编排器：文档说明 |

## docs/media

README 中使用的实机视频、动图和编排器截图

| 文件 | 用途说明 |
|---|---|
| [README.md](../docs/media/README.md) | README 中使用的实机视频、动图和编排器截图：使用说明与当前目录文件导航 |
| [multitrack-composer.png](../docs/media/multitrack-composer.png) | 多轨编排器真实截图，展示飞吻组合的动作与表情衔接 |
| [robot-demo-preview.gif](../docs/media/robot-demo-preview.gif) | 实机视频的 6 秒无声节选，用于 README 自动播放 |
| [robot-demo.mp4](../docs/media/robot-demo.mp4) | 用户提供的原始实机展示视频，约 24 秒，保留原音轨 |

## expressions

机身动画分区构建输入

| 文件 | 用途说明 |
|---|---|
| [README.md](../expressions/README.md) | 机身动画分区构建输入：使用说明与当前目录文件导航 |

## expressions/official

官方精简与头屏表情分区镜像

| 文件 | 用途说明 |
|---|---|
| [README.md](../expressions/official/README.md) | 官方精简与头屏表情分区镜像：使用说明与当前目录文件导航 |
| [all_emote_assets.bin](../expressions/official/all_emote_assets.bin) | 固件 CMake 构建引用的动画分区输入，与 flash 中同名镜像一致 |

## firmware

ESP32-S3 板端源码、分区和构建配置

| 文件 | 用途说明 |
|---|---|
| [CMakeLists.txt](../firmware/CMakeLists.txt) | ESP-IDF 固件工程的顶层构建入口 |
| [README.md](../firmware/README.md) | ESP32-S3 板端源码、分区和构建配置：使用说明与当前目录文件导航 |
| [dependencies.lock](../firmware/dependencies.lock) | ESP-IDF 组件版本与校验锁定文件，由组件管理器维护 |
| [partitions.csv](../firmware/partitions.csv) | Flash 分区布局：程序、存储和表情动画分区等 |
| [sdkconfig.defaults](../firmware/sdkconfig.defaults) | 固件基础默认构建配置 |
| [sdkconfig.demo](../firmware/sdkconfig.demo) | 演示固件的完整 ESP-IDF 配置快照 |
| [sdkconfig.emote](../firmware/sdkconfig.emote) | 表情固件的完整 ESP-IDF 配置快照 |
| [sdkconfig.emote.defaults](../firmware/sdkconfig.emote.defaults) | 表情播放器编译验证配置，默认禁用舵机输出，需核对候选引脚 |
| [sdkconfig.network-camera.defaults](../firmware/sdkconfig.network-camera.defaults) | 带摄像头候选主板的联网默认配置，Wi-Fi 使用占位符，需实机核对 |
| [sdkconfig.network-no-camera.defaults](../firmware/sdkconfig.network-no-camera.defaults) | 无摄像头主板的联网默认配置，Wi-Fi 使用占位符 |

## firmware/assets

storage 分区打包输入；不含完整表情动画分区

| 文件 | 用途说明 |
|---|---|
| [README.md](../firmware/assets/README.md) | storage 分区打包输入；不含完整表情动画分区：使用说明与当前目录文件导航 |
| [README.txt](../firmware/assets/README.txt) | storage 与 emote_gen 分区资源边界及动作表情数据入口说明 |

## firmware/components

ESP-IDF 本地组件与兼容层

| 文件 | 用途说明 |
|---|---|
| [README.md](../firmware/components/README.md) | ESP-IDF 本地组件与兼容层：使用说明与当前目录文件导航 |

## firmware/components/json

旧 json 组件名到 espressif__cjson 的兼容层

| 文件 | 用途说明 |
|---|---|
| [CMakeLists.txt](../firmware/components/json/CMakeLists.txt) | 将 json 组件依赖转接给 espressif__cjson |
| [README.md](../firmware/components/json/README.md) | 旧 json 组件名到 espressif__cjson 的兼容层：使用说明与当前目录文件导航 |

## firmware/main

主控启动、四舵机、屏幕、音频和无线协议

| 文件 | 用途说明 |
|---|---|
| [CMakeLists.txt](../firmware/main/CMakeLists.txt) | 注册主控源文件、声明组件依赖并构建 storage 和动画资源分区 |
| [Kconfig.projbuild](../firmware/main/Kconfig.projbuild) | ESP-IDF menuconfig 中的主板、网络、表情与舵机配置项 |
| [README.md](../firmware/main/README.md) | 主控启动、四舵机、屏幕、音频和无线协议：使用说明与当前目录文件导航 |
| [audio_input.cpp](../firmware/main/audio_input.cpp) | 麦克风音频采集的实现 |
| [audio_input.hpp](../firmware/main/audio_input.hpp) | 麦克风音频采集的接口声明 |
| [audio_output.cpp](../firmware/main/audio_output.cpp) | 扬声器音频播放的实现 |
| [audio_output.hpp](../firmware/main/audio_output.hpp) | 扬声器音频播放的接口声明 |
| [behavior.cpp](../firmware/main/behavior.cpp) | 动作程序解析、执行时序与分段调度的实现 |
| [behavior.hpp](../firmware/main/behavior.hpp) | 动作程序解析、执行时序与分段调度的接口声明 |
| [behavior_model.hpp](../firmware/main/behavior_model.hpp) | 动作帧、分段与组合程序等数据结构及辅助逻辑 |
| [ble_control.cpp](../firmware/main/ble_control.cpp) | BLE 广播、连接与控制指令通道的实现 |
| [ble_control.hpp](../firmware/main/ble_control.hpp) | BLE 广播、连接与控制指令通道的接口声明 |
| [board_display.cpp](../firmware/main/board_display.cpp) | 屏幕初始化、图像绘制与显示方向处理的实现 |
| [board_display.hpp](../firmware/main/board_display.hpp) | 屏幕初始化、图像绘制与显示方向处理的接口声明 |
| [board_profile.hpp](../firmware/main/board_profile.hpp) | 主板类型和 GPIO 定义，包括舵机与屏幕引脚 |
| [idf_component.yml](../firmware/main/idf_component.yml) | 主控组件所需的 ESP-IDF 第三方依赖声明 |
| [main.cpp](../firmware/main/main.cpp) | 固件启动入口与主任务的实现 |
| [motion_types.hpp](../firmware/main/motion_types.hpp) | 四轴舵机姿态 Pose 的类型定义 |
| [otto_motion.cpp](../firmware/main/otto_motion.cpp) | 四舵机 PWM 输出、姿态插值与周期摆动的实现 |
| [otto_motion.hpp](../firmware/main/otto_motion.hpp) | 四舵机 PWM 输出、姿态插值与周期摆动的接口声明 |
| [protocol.cpp](../firmware/main/protocol.cpp) | 机器人控制协议、指令解析与状态响应的实现 |
| [protocol.hpp](../firmware/main/protocol.hpp) | 机器人控制协议、指令解析与状态响应的接口声明 |
| [robot.cpp](../firmware/main/robot.cpp) | 机器人模块初始化、状态和整体协调的实现 |
| [robot.hpp](../firmware/main/robot.hpp) | 机器人模块初始化、状态和整体协调的接口声明 |
| [robot_face.cpp](../firmware/main/robot_face.cpp) | 表情动画选择、播放与循环控制的实现 |
| [robot_face.hpp](../firmware/main/robot_face.hpp) | 表情动画选择、播放与循环控制的接口声明 |
| [wifi_http.cpp](../firmware/main/wifi_http.cpp) | Wi-Fi 初始化及 HTTP 控制服务的实现 |
| [wifi_http.hpp](../firmware/main/wifi_http.hpp) | Wi-Fi 初始化及 HTTP 控制服务的接口声明 |

## flash

公开刷机文件、写入地址与镜像校验信息

| 文件 | 用途说明 |
|---|---|
| [README.md](../flash/README.md) | 公开刷机文件、写入地址与镜像校验信息：使用说明与当前目录文件导航 |
| [all_emote_assets.bin](../flash/all_emote_assets.bin) | 官方精简及 32 个头屏表情分区镜像，写入 0x800000 |
| [bootloader.bin](../flash/bootloader.bin) | 公开固件引导程序，写入 0x0 |
| [manifest.json](../flash/manifest.json) | 公开固件构建来源、写入地址和每个镜像的 SHA256 |
| [otto_expression_motion.bin](../flash/otto_expression_motion.bin) | 不含私人网络配置的公开主程序，写入 0x20000 |
| [partition-table.bin](../flash/partition-table.bin) | 16 MB Flash 分区表，写入 0x8000 |
| [storage.bin](../flash/storage.bin) | storage SPIFFS 分区镜像，写入 0x700000 |

## gesture_recognition

电脑摄像头识别、手势映射和指令发送

| 文件 | 用途说明 |
|---|---|
| [README.md](../gesture_recognition/README.md) | 电脑摄像头识别、手势映射和指令发送：使用说明与当前目录文件导航 |
| [gesture_actions.json](../gesture_recognition/gesture_actions.json) | 手势对应动作与组合 ID：枪形侧倒、拳头后退、V 前进等 |
| [motion_bridge.py](../gesture_recognition/motion_bridge.py) | 手势别名归一化、动作冷却、设备身份核验与 HTTP 指令发送 |
| [recognize.py](../gesture_recognition/recognize.py) | 笔记本摄像头识别入口：YOLO 推理、类别显示、稳定判定及可选机器人响应 |
| [robot_config.py](../gesture_recognition/robot_config.py) | 统一读取本地配置和环境变量，按仓库位置解析模型路径 |
| [test_motion_bridge.py](../gesture_recognition/test_motion_bridge.py) | 手势映射、冷却、停止优先级、设备核验和组合调用测试 |
| [test_recognize.py](../gesture_recognition/test_recognize.py) | 识别稳定判定、手势候选与确认逻辑测试 |
| [test_video_input.py](../gesture_recognition/test_video_input.py) | 网页视频接入与识别流程的手势侧测试 |
| [video_worker.py](../gesture_recognition/video_worker.py) | 网页视频推理子进程：接收图像帧并返回手势识别结果 |

## licenses

随项目保留的上游许可文本

| 文件 | 用途说明 |
|---|---|
| [OttoDIYLib-LICENSE.txt](../licenses/OttoDIYLib-LICENSE.txt) | OttoDIYLib 动作算法上游 GPL-3.0 许可文本 |
| [README.md](../licenses/README.md) | 随项目保留的上游许可文本：使用说明与当前目录文件导航 |
| [esp-emote-gfx-LICENSE.txt](../licenses/esp-emote-gfx-LICENSE.txt) | Espressif 表情图形组件上游许可文本 |

## models

GitHub Releases 手势模型下载说明

| 文件 | 用途说明 |
|---|---|
| [README.md](../models/README.md) | GitHub Releases 手势模型下载说明：使用说明与当前目录文件导航 |

## tools

模型下载、资源迁移、环境检查和便携包工具

| 文件 | 用途说明 |
|---|---|
| [README.md](../tools/README.md) | 模型下载、资源迁移、环境检查和便携包工具：使用说明与当前目录文件导航 |
| [bootstrap_runtime.ps1](../tools/bootstrap_runtime.ps1) | 源码包首次双击启动时下载、校验并安装 Windows 运行环境与模型 |
| [build_handoff.py](../tools/build_handoff.py) | 收集源码、模型、素材及 Python 运行库，生成 Windows 同事交接 ZIP |
| [check_environment.py](../tools/check_environment.py) | 检查 Python 依赖、模型目录及组合引用的音频，不发送机器人动作 |
| [download_models.py](../tools/download_models.py) | 从本项目 GitHub Releases 下载并校验已验证的手势与语音模型 |
| [portable_launcher.py](../tools/portable_launcher.py) | 便携包启动器：选择空闲端口、启动服务、打开浏览器；支持无动作启动检查 |
| [resources.py](../tools/resources.py) | 导入或导出声音和个人动作覆盖 ZIP，拒绝覆盖已有文件 |
| [update_file_index.py](../tools/update_file_index.py) | 维护中文文件索引，按配置说明及组合、表情元数据生成各级 README 导航 |
| [windows_tts.ps1](../tools/windows_tts.ps1) | 调用 Windows System.Speech 将中文文本合成为 WAV |

## voice-model

GitHub Releases 离线语音模型下载说明

| 文件 | 用途说明 |
|---|---|
| [README.md](../voice-model/README.md) | GitHub Releases 离线语音模型下载说明：使用说明与当前目录文件导航 |

## web

网页服务、多轨组合、语音识别和机器人通信

| 文件 | 用途说明 |
|---|---|
| [README.md](../web/README.md) | 网页服务、多轨组合、语音识别和机器人通信：使用说明与当前目录文件导航 |
| [audio_tools.py](../web/audio_tools.py) | 查找系统 FFmpeg，或回退到 Python 依赖内置的 FFmpeg |
| [ble_link.py](../web/ble_link.py) | BLE 扫描、连接、指令收发与断线恢复 |
| [composer_store.py](../web/composer_store.py) | 管理组合与音频的保存、校验、上传、合成、资源快照和触发词匹配 |
| [requirements.txt](../web/requirements.txt) | 网页后端的基础 Python 依赖，根目录依赖清单会引用此文件 |
| [server.py](../web/server.py) | 本地 HTTP 服务入口，提供控制接口、资源目录及组合执行调度 |
| [video_input.py](../web/video_input.py) | 管理浏览器视频帧和识别子进程，将识别结果接入动作与组合调度 |
| [voice_trigger.py](../web/voice_trigger.py) | 离线语音转写、唤醒词与关键词监听，触发对应组合 |

## web/library

已保存组合以及本地声音资源

| 文件 | 用途说明 |
|---|---|
| [README.md](../web/library/README.md) | 已保存组合以及本地声音资源：使用说明与当前目录文件导航 |

## web/library/audio

随项目提供的演示音频与声音元数据

| 文件 | 用途说明 |
|---|---|
| [24ca1543-fb78-4760-b22e-e0d2824ca034-fa5aba8532e3488f97467f4e0e9664a6.wav](../web/library/audio/24ca1543-fb78-4760-b22e-e0d2824ca034-fa5aba8532e3488f97467f4e0e9664a6.wav) | “收到”的WAV音频；可能被已保存组合的资源快照引用 |
| [24ca1543-fb78-4760-b22e-e0d2824ca034.json](../web/library/audio/24ca1543-fb78-4760-b22e-e0d2824ca034.json) | 声音“收到”的元数据：音频地址、时长、来源和校验值 |
| [2ea554c7-61af-4f7f-bb5a-200d165df51f-4aaa5fe21fa4430f8aae053822255dd9.wav](../web/library/audio/2ea554c7-61af-4f7f-bb5a-200d165df51f-4aaa5fe21fa4430f8aae053822255dd9.wav) | “哼”的WAV音频；可能被已保存组合的资源快照引用 |
| [2ea554c7-61af-4f7f-bb5a-200d165df51f-851171f46bdd4bacb11aea43fc1cda97.wav](../web/library/audio/2ea554c7-61af-4f7f-bb5a-200d165df51f-851171f46bdd4bacb11aea43fc1cda97.wav) | “哼”的WAV音频；可能被已保存组合的资源快照引用 |
| [2ea554c7-61af-4f7f-bb5a-200d165df51f-f8d3c9e1e18e45fda0a0bfaea8b22fb9.wav](../web/library/audio/2ea554c7-61af-4f7f-bb5a-200d165df51f-f8d3c9e1e18e45fda0a0bfaea8b22fb9.wav) | “哼”的WAV音频；可能被已保存组合的资源快照引用 |
| [2ea554c7-61af-4f7f-bb5a-200d165df51f.json](../web/library/audio/2ea554c7-61af-4f7f-bb5a-200d165df51f.json) | 声音“哼”的元数据：音频地址、时长、来源和校验值 |
| [378f3723-b131-45cc-acc1-2a41acc77862-3f535350e03c447ebd72c86a8cf478ef.wav](../web/library/audio/378f3723-b131-45cc-acc1-2a41acc77862-3f535350e03c447ebd72c86a8cf478ef.wav) | “节拍舞曲-grok”的WAV音频；可能被已保存组合的资源快照引用 |
| [378f3723-b131-45cc-acc1-2a41acc77862.json](../web/library/audio/378f3723-b131-45cc-acc1-2a41acc77862.json) | 声音“节拍舞曲-grok”的元数据：音频地址、时长、来源和校验值 |
| [3dcf8939-a5d4-456d-ac79-64b4f549b9ed-7ec5169e8804427b8aecaaa68a9d8c99.wav](../web/library/audio/3dcf8939-a5d4-456d-ac79-64b4f549b9ed-7ec5169e8804427b8aecaaa68a9d8c99.wav) | “不跟你玩了！”的WAV音频；可能被已保存组合的资源快照引用 |
| [3dcf8939-a5d4-456d-ac79-64b4f549b9ed.json](../web/library/audio/3dcf8939-a5d4-456d-ac79-64b4f549b9ed.json) | 声音“不跟你玩了！”的元数据：音频地址、时长、来源和校验值 |
| [5144d03f-10dc-423f-bd38-e3ec2d999bcd-4457582d4a6844b5bc7a91e6f913882c.wav](../web/library/audio/5144d03f-10dc-423f-bd38-e3ec2d999bcd-4457582d4a6844b5bc7a91e6f913882c.wav) | “爱你”的WAV音频；可能被已保存组合的资源快照引用 |
| [5144d03f-10dc-423f-bd38-e3ec2d999bcd.json](../web/library/audio/5144d03f-10dc-423f-bd38-e3ec2d999bcd.json) | 声音“爱你”的元数据：音频地址、时长、来源和校验值 |
| [85f44317-0a32-438f-9826-9c7794f694c3-7906bc300da94683a9cc69ff208878fa.wav](../web/library/audio/85f44317-0a32-438f-9826-9c7794f694c3-7906bc300da94683a9cc69ff208878fa.wav) | “我来啦”的WAV音频；可能被已保存组合的资源快照引用 |
| [85f44317-0a32-438f-9826-9c7794f694c3.json](../web/library/audio/85f44317-0a32-438f-9826-9c7794f694c3.json) | 声音“我来啦”的元数据：音频地址、时长、来源和校验值 |
| [8a486d5d-e338-4cf4-9013-1f1eb17a7512-64a6b9d6c4ec457ea708f53987ecc506.wav](../web/library/audio/8a486d5d-e338-4cf4-9013-1f1eb17a7512-64a6b9d6c4ec457ea708f53987ecc506.wav) | “奥托问候”的WAV音频；可能被已保存组合的资源快照引用 |
| [8a486d5d-e338-4cf4-9013-1f1eb17a7512-6a24324e63394bdd8095454303a18bba.wav](../web/library/audio/8a486d5d-e338-4cf4-9013-1f1eb17a7512-6a24324e63394bdd8095454303a18bba.wav) | “奥托问候”的WAV音频；可能被已保存组合的资源快照引用 |
| [8a486d5d-e338-4cf4-9013-1f1eb17a7512-e9ee5b3dd8be422f9f6230a0edb6a31b.wav](../web/library/audio/8a486d5d-e338-4cf4-9013-1f1eb17a7512-e9ee5b3dd8be422f9f6230a0edb6a31b.wav) | “奥托问候”的WAV音频；可能被已保存组合的资源快照引用 |
| [8a486d5d-e338-4cf4-9013-1f1eb17a7512-fe898dd3fde0477789e2f9ddc9640394.wav](../web/library/audio/8a486d5d-e338-4cf4-9013-1f1eb17a7512-fe898dd3fde0477789e2f9ddc9640394.wav) | “奥托问候”的WAV音频；可能被已保存组合的资源快照引用 |
| [8a486d5d-e338-4cf4-9013-1f1eb17a7512.json](../web/library/audio/8a486d5d-e338-4cf4-9013-1f1eb17a7512.json) | 声音“奥托问候”的元数据：音频地址、时长、来源和校验值 |
| [README.md](../web/library/audio/README.md) | 随项目提供的演示音频与声音元数据：使用说明与当前目录文件导航 |
| [b7611b9b-5f08-4979-bb83-a91f4e5c0065-87a64d0937ff422885232bff5a15bb11.wav](../web/library/audio/b7611b9b-5f08-4979-bb83-a91f4e5c0065-87a64d0937ff422885232bff5a15bb11.wav) | “10月10日”的WAV音频；可能被已保存组合的资源快照引用 |
| [b7611b9b-5f08-4979-bb83-a91f4e5c0065.json](../web/library/audio/b7611b9b-5f08-4979-bb83-a91f4e5c0065.json) | 声音“10月10日”的元数据：音频地址、时长、来源和校验值 |
| [fc05cec8-c025-4423-8694-b678a3b90eb8-70d392f13bd94b9a8cd70d2af558124c.wav](../web/library/audio/fc05cec8-c025-4423-8694-b678a3b90eb8-70d392f13bd94b9a8cd70d2af558124c.wav) | “那可不”的WAV音频；可能被已保存组合的资源快照引用 |
| [fc05cec8-c025-4423-8694-b678a3b90eb8.json](../web/library/audio/fc05cec8-c025-4423-8694-b678a3b90eb8.json) | 声音“那可不”的元数据：音频地址、时长、来源和校验值 |
| [爱你.mp3](../web/library/audio/%E7%88%B1%E4%BD%A0.mp3) | “爱你”的MP3音频；可能被已保存组合的资源快照引用 |

## web/library/compositions

按 UUID 保存的动作、表情、声音多轨组合

| 文件 | 用途说明 |
|---|---|
| [1a3b49e1-025a-44b5-8c7f-4aebac8b584f.json](../web/library/compositions/1a3b49e1-025a-44b5-8c7f-4aebac8b584f.json) | 组合“飞吻”：6 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [27f94610-0a42-4794-bad3-be5c2456c006.json](../web/library/compositions/27f94610-0a42-4794-bad3-be5c2456c006.json) | 组合“才艺展示”：10 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [2e714c00-e7a0-4c07-939a-2d5677496d9f.json](../web/library/compositions/2e714c00-e7a0-4c07-939a-2d5677496d9f.json) | 组合“变僵尸”：7 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [3884bed2-4da5-4873-9d10-3e53f71ee72c.json](../web/library/compositions/3884bed2-4da5-4873-9d10-3e53f71ee72c.json) | 组合“我伤心了”：5 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [389da23e-4726-4841-b1f6-c19239c87168.json](../web/library/compositions/389da23e-4726-4841-b1f6-c19239c87168.json) | 组合“往前走”：6 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [3958423e-475d-40c9-a9ef-657ecb801b51.json](../web/library/compositions/3958423e-475d-40c9-a9ef-657ecb801b51.json) | 组合“变小狗”：8 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [44d0963e-7dc9-4570-a13a-1782962c93bf.json](../web/library/compositions/44d0963e-7dc9-4570-a13a-1782962c93bf.json) | 组合“生气”：5 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [462c2ce4-2140-4fa4-9167-ee4efcd920cd.json](../web/library/compositions/462c2ce4-2140-4fa4-9167-ee4efcd920cd.json) | 组合“爱你-grok版”：35 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [472e7c83-1ffd-4285-8a2d-102dc38e5da1.json](../web/library/compositions/472e7c83-1ffd-4285-8a2d-102dc38e5da1.json) | 组合“爱你”：32 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [68cd6661-2824-4b81-b1e5-588ded7b1404.json](../web/library/compositions/68cd6661-2824-4b81-b1e5-588ded7b1404.json) | 组合“击鼓”：9 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [73f9657e-a693-45ac-9020-6d888b41fe14.json](../web/library/compositions/73f9657e-a693-45ac-9020-6d888b41fe14.json) | 组合“我累了”：4 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [7f39a4ca-2ee1-44a8-95f4-094bc7b18447.json](../web/library/compositions/7f39a4ca-2ee1-44a8-95f4-094bc7b18447.json) | 组合“好吃”：2 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [8406761d-b7ef-407a-ab4b-1e039e10810d.json](../web/library/compositions/8406761d-b7ef-407a-ab4b-1e039e10810d.json) | 组合“编排示例：归位＋微笑”：4 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [8b9e9cf8-6e13-4913-887a-3a6e3154ec3e.json](../web/library/compositions/8b9e9cf8-6e13-4913-887a-3a6e3154ec3e.json) | 组合“摆造型”：5 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [9a0bfe34-bbd1-4da9-9bac-9f270bad120f.json](../web/library/compositions/9a0bfe34-bbd1-4da9-9bac-9f270bad120f.json) | 组合“开心”：5 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [9abb77c9-e4d7-4817-be03-19612976d624.json](../web/library/compositions/9abb77c9-e4d7-4817-be03-19612976d624.json) | 组合“吹小号”：8 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [README.md](../web/library/compositions/README.md) | 按 UUID 保存的动作、表情、声音多轨组合：使用说明与当前目录文件导航 |
| [a02b547d-0df4-4a68-afdc-a92351ef40fa.json](../web/library/compositions/a02b547d-0df4-4a68-afdc-a92351ef40fa.json) | 组合“你是笨蛋”：8 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [a1cd58a0-74a2-4b2d-a92a-a5cd90637dfc.json](../web/library/compositions/a1cd58a0-74a2-4b2d-a92a-a5cd90637dfc.json) | 组合“爱你-grok版-纠偏”：33 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [a7e82bcf-1ff4-43be-a5a8-b3aac4a6e61b.json](../web/library/compositions/a7e82bcf-1ff4-43be-a5a8-b3aac4a6e61b.json) | 组合“爱你·电脑播歌”：32 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [a9f7aee0-75e5-460f-9248-b426a92b2f4c.json](../web/library/compositions/a9f7aee0-75e5-460f-9248-b426a92b2f4c.json) | 组合“机身语音联调”：3 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [b493e93b-4382-460b-ba60-107343250c26.json](../web/library/compositions/b493e93b-4382-460b-ba60-107343250c26.json) | 组合“我生气了”：5 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [b5eeb062-e4e4-4091-9bd7-fb95c9155697.json](../web/library/compositions/b5eeb062-e4e4-4091-9bd7-fb95c9155697.json) | 组合“变小猫”：7 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [b7cf7310-2833-4310-978b-6f85a1cafcca.json](../web/library/compositions/b7cf7310-2833-4310-978b-6f85a1cafcca.json) | 组合“弹钢琴”：8 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [d4c6c743-1bec-4281-96c4-4b2e3e5f8472.json](../web/library/compositions/d4c6c743-1bec-4281-96c4-4b2e3e5f8472.json) | 组合“爱你-grok原创-纠偏”：2 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [dd435784-b519-4a40-aff1-52b8cada58d2.json](../web/library/compositions/dd435784-b519-4a40-aff1-52b8cada58d2.json) | 组合“爱你·快舞”：33 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [df457493-bdc7-49d4-956b-bfc1490b6fe9.json](../web/library/compositions/df457493-bdc7-49d4-956b-bfc1490b6fe9.json) | 组合“转圈”：6 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [e965db59-a538-4ec7-a06a-078cada430b1.json](../web/library/compositions/e965db59-a538-4ec7-a06a-078cada430b1.json) | 组合“往后退”：4 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [f8b022c9-683f-4209-a9ce-b3077d71be31.json](../web/library/compositions/f8b022c9-683f-4209-a9ce-b3077d71be31.json) | 组合“跳舞”：14 个片段；保存各轨时间与资源快照，文件名为组合 UUID |
| [fb20433b-f1ca-4531-9c9d-703ee6df8f40.json](../web/library/compositions/fb20433b-f1ca-4531-9c9d-703ee6df8f40.json) | 组合“爱你-grok原创”：2 个片段；保存各轨时间与资源快照，文件名为组合 UUID |

## web/static

浏览器页面、样式、交互脚本和动作表情目录

| 文件 | 用途说明 |
|---|---|
| [README.md](../web/static/README.md) | 浏览器页面、样式、交互脚本和动作表情目录：使用说明与当前目录文件导航 |
| [actions.json](../web/static/actions.json) | 可编辑的四舵机动作库，含角度、幅度、周期、时长和节奏变体 |
| [app.js](../web/static/app.js) | 控制台交互：连接、状态刷新、动作编辑、舵机姿态与表情播放 |
| [camera_labels.js](../web/static/camera_labels.js) | 控制台摄像头采集、视频帧上传及识别标签显示 |
| [composer.css](../web/static/composer.css) | 多轨编排器布局、轨道、片段与属性面板样式 |
| [composer.html](../web/static/composer.html) | 多轨编排器页面：组合列表、资源库、预览、属性面板及时间轴 |
| [composer.js](../web/static/composer.js) | 多轨拖放、吸附、片段编辑、预览、保存、撤销及实机组合运行 |
| [concepts.css](../web/static/concepts.css) | 彩色概念表情预览页面样式 |
| [concepts.json](../web/static/concepts.json) | 彩色概念表情的名称、ID 和预览目录 |
| [dashboard.css](../web/static/dashboard.css) | 控制台面板和资源展示的补充样式 |
| [emo-preview.html](../web/static/emo-preview.html) | 彩色概念表情的独立展示预览页面 |
| [expressions.json](../web/static/expressions.json) | 表情 ID、中文名称、预览、时长及分段循环元数据目录 |
| [index.html](../web/static/index.html) | 机器人控制台页面：连接方式、舵机调试、动作和表情库 |
| [source_modes.css](../web/static/source_modes.css) | 输入来源切换、识别状态和相关控件样式 |
| [source_modes.js](../web/static/source_modes.js) | 编排器语音/视频输入模式切换、摄像头上传和状态交互 |
| [styles.css](../web/static/styles.css) | 控制台基础布局、颜色、按钮和组件样式 |

## web/static/concepts

彩色眼镜、面罩等概念表情预览

| 文件 | 用途说明 |
|---|---|
| [README.md](../web/static/concepts/README.md) | 彩色眼镜、面罩等概念表情预览：使用说明与当前目录文件导航 |
| [cycling_goggles.gif](../web/static/concepts/cycling_goggles.gif) | “骑行风镜”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [hero_mask.gif](../web/static/concepts/hero_mask.gif) | “超级英雄”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [neon_shades.gif](../web/static/concepts/neon_shades.gif) | “霓虹墨镜”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [rainbow_party.gif](../web/static/concepts/rainbow_party.gif) | “彩虹派对”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [science_goggles.gif](../web/static/concepts/science_goggles.gif) | “科学护目镜”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [space_visor.gif](../web/static/concepts/space_visor.gif) | “宇航面罩”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [目录说明.md](../web/static/concepts/%E7%9B%AE%E5%BD%95%E8%AF%B4%E6%98%8E.md) | 彩色表情预览：文档说明 |

## web/static/official

表情 GIF、缩略视频与候选素材

| 文件 | 用途说明 |
|---|---|
| [README.md](../web/static/official/README.md) | 表情 GIF、缩略视频与候选素材：使用说明与当前目录文件导航 |
| [angry_20s.gif](../web/static/official/angry_20s.gif) | “生气”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [asleep_215s.gif](../web/static/official/asleep_215s.gif) | “睡着”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [awkward_xx.gif](../web/static/official/awkward_xx.gif) | “尴尬尬笑”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [badminton_12.gif](../web/static/official/badminton_12.gif) | “羽毛球”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [bird_act.gif](../web/static/official/bird_act.gif) | “变小鸟”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [bliss_bub.gif](../web/static/official/bliss_bub.gif) | “幸福泡泡”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [burp_xx.gif](../web/static/official/burp_xx.gif) | “打嗝”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [cat_act.gif](../web/static/official/cat_act.gif) | “变小猫”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [charge_xx.gif](../web/static/official/charge_xx.gif) | “充电回血”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [confident_08.gif](../web/static/official/confident_08.gif) | “自信”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [cry_10s_10s.gif](../web/static/official/cry_10s_10s.gif) | “哭泣”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [dog_act.gif](../web/static/official/dog_act.gif) | “变小狗”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [drums_act.gif](../web/static/official/drums_act.gif) | “打鼓”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [glasses_xx.gif](../web/static/official/glasses_xx.gif) | “眼镜反光”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [guitar_act.gif](../web/static/official/guitar_act.gif) | “弹吉他”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [heart_hands.gif](../web/static/official/heart_hands.gif) | “比心”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [hello_wave.gif](../web/static/official/hello_wave.gif) | “招手你好”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [idea_bulb.gif](../web/static/official/idea_bulb.gif) | “灵感灯泡”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [investigate_.gif](../web/static/official/investigate_.gif) | “观察”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [kiss_act.gif](../web/static/official/kiss_act.gif) | “飞吻”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [laugh_05s_10.gif](../web/static/official/laugh_05s_10.gif) | “大笑”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [leisure_05s_.gif](../web/static/official/leisure_05s_.gif) | “悠闲”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [lightning_xx.gif](../web/static/official/lightning_xx.gif) | “被雷劈”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [magic_act.gif](../web/static/official/magic_act.gif) | “变魔术”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [mock_05s.gif](../web/static/official/mock_05s.gif) | “调皮”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [music_25s.gif](../web/static/official/music_25s.gif) | “弹钢琴”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [mute_05s.gif](../web/static/official/mute_05s.gif) | “无语”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [nap_zzz.gif](../web/static/official/nap_zzz.gif) | “打瞌睡”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [no_shake.gif](../web/static/official/no_shake.gif) | “摇头拒绝”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [panda_act.gif](../web/static/official/panda_act.gif) | “变熊猫”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [panic_05s_15.gif](../web/static/official/panic_05s_15.gif) | “慌张”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [party_xx.gif](../web/static/official/party_xx.gif) | “中彩票撒花”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [ponder_05s.gif](../web/static/official/ponder_05s.gif) | “思考”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [question_05s.gif](../web/static/official/question_05s.gif) | “疑问”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [rabbit_act.gif](../web/static/official/rabbit_act.gif) | “变兔子”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [rain_sad.gif](../web/static/official/rain_sad.gif) | “下雨撑伞”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [sad_05s15s.gif](../web/static/official/sad_05s15s.gif) | “难过”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [shocked_05s_.gif](../web/static/official/shocked_05s_.gif) | “震惊”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [shot_die.gif](../web/static/official/shot_die.gif) | “中弹碎裂”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [shy_20s_40s.gif](../web/static/official/shy_20s_40s.gif) | “害羞”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [sigh_20s_20s.gif](../web/static/official/sigh_20s_20s.gif) | “叹气”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [smile_05s.gif](../web/static/official/smile_05s.gif) | “微笑”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [smile_static.gif](../web/static/official/smile_static.gif) | “静态微笑”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [smug_xx.gif](../web/static/official/smug_xx.gif) | “得意挑眉”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [sneeze_xx.gif](../web/static/official/sneeze_xx.gif) | “打喷嚏”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [snigger_10s.gif](../web/static/official/snigger_10s.gif) | “窃笑”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [sob_flood.gif](../web/static/official/sob_flood.gif) | “泪水喷涌”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [soul_out.gif](../web/static/official/soul_out.gif) | “灵魂出窍”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [steam_mad.gif](../web/static/official/steam_mad.gif) | “冒蒸汽怒”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [sulk_act.gif](../web/static/official/sulk_act.gif) | “超级委屈”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [trumpet_act.gif](../web/static/official/trumpet_act.gif) | “吹喇叭”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [wink_xx.gif](../web/static/official/wink_xx.gif) | “眨眼挑逗”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [yawn_20s.gif](../web/static/official/yawn_20s.gif) | “哈欠”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [yes_bounce.gif](../web/static/official/yes_bounce.gif) | “大力点头”的 GIF 网页预览；机身播放仍需对应固件动画资源 |
| [yummy_20_s.gif](../web/static/official/yummy_20_s.gif) | “美味”的 GIF 网页预览；机身播放仍需对应固件动画资源 |

## web/static/official/_drafts

待筛选的表情关键帧与打包候选稿

| 文件 | 用途说明 |
|---|---|
| [README.md](../web/static/official/_drafts/README.md) | 待筛选的表情关键帧与打包候选稿：使用说明与当前目录文件导航 |

## web/static/official/_drafts/head_only

头屏关键帧、过渡帧与视觉检查图

| 文件 | 用途说明 |
|---|---|
| [PROMPT_GUIDE.md](../web/static/official/_drafts/head_only/PROMPT_GUIDE.md) | 生图提示词指南（头屏专用）：文档说明 |
| [README.md](../web/static/official/_drafts/head_only/README.md) | 头屏关键帧、过渡帧与视觉检查图：使用说明与当前目录文件导航 |
| [_pending_ids.json](../web/static/official/_drafts/head_only/_pending_ids.json) | 候选表情的隔离/待确认 ID 清单，不代表已烧录到机身 |
| [_qa_seed_strip.png](../web/static/official/_drafts/head_only/_qa_seed_strip.png) | 关键帧候选素材拼图，供视觉检查与对照 |
| [awkward_xx_head_01.jpg](../web/static/official/_drafts/head_only/awkward_xx_head_01.jpg) | “尴尬尬笑”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [bird_act_head_01.jpg](../web/static/official/_drafts/head_only/bird_act_head_01.jpg) | “变小鸟”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [bliss_bub_head_01.png](../web/static/official/_drafts/head_only/bliss_bub_head_01.png) | “幸福泡泡”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [burp_xx_head_01.jpg](../web/static/official/_drafts/head_only/burp_xx_head_01.jpg) | “打嗝”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [cat_act_head_01.png](../web/static/official/_drafts/head_only/cat_act_head_01.png) | “变小猫”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [cat_act_loop_01.png](../web/static/official/_drafts/head_only/cat_act_loop_01.png) | “变小猫”循环关键帧，用于表情制作，不是可直接烧录的动画包 |
| [charge_xx_head_01.jpg](../web/static/official/_drafts/head_only/charge_xx_head_01.jpg) | “充电回血”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [dog_act_head_01.jpg](../web/static/official/_drafts/head_only/dog_act_head_01.jpg) | “变小狗”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [dog_act_loop_01.png](../web/static/official/_drafts/head_only/dog_act_loop_01.png) | “变小狗”循环关键帧，用于表情制作，不是可直接烧录的动画包 |
| [drums_act_head_01.jpg](../web/static/official/_drafts/head_only/drums_act_head_01.jpg) | “打鼓”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [glasses_xx_head_01.jpg](../web/static/official/_drafts/head_only/glasses_xx_head_01.jpg) | “眼镜反光”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [guitar_act_head_01.jpg](../web/static/official/_drafts/head_only/guitar_act_head_01.jpg) | “弹吉他”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [heart_hands_head_01.jpg](../web/static/official/_drafts/head_only/heart_hands_head_01.jpg) | “比心”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [hello_wave_head_01.jpg](../web/static/official/_drafts/head_only/hello_wave_head_01.jpg) | “招手你好”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [idea_bulb_head_01.jpg](../web/static/official/_drafts/head_only/idea_bulb_head_01.jpg) | “灵感灯泡”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [kiss_act_head_01.jpg](../web/static/official/_drafts/head_only/kiss_act_head_01.jpg) | “飞吻”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [lightning_xx_head_01.jpg](../web/static/official/_drafts/head_only/lightning_xx_head_01.jpg) | “被雷劈”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [magic_act_head_01.jpg](../web/static/official/_drafts/head_only/magic_act_head_01.jpg) | “变魔术”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [music_25s_head_01.jpg](../web/static/official/_drafts/head_only/music_25s_head_01.jpg) | “弹钢琴”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [nap_zzz_head_01.jpg](../web/static/official/_drafts/head_only/nap_zzz_head_01.jpg) | “打瞌睡”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [no_shake_head_01.jpg](../web/static/official/_drafts/head_only/no_shake_head_01.jpg) | “摇头拒绝”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [panda_act_head_01.jpg](../web/static/official/_drafts/head_only/panda_act_head_01.jpg) | “变熊猫”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [party_xx_head_01.jpg](../web/static/official/_drafts/head_only/party_xx_head_01.jpg) | “中彩票撒花”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [qa_shot_f0_smile.png](../web/static/official/_drafts/head_only/qa_shot_f0_smile.png) | 中弹表情视觉检查帧：f0_smile（帧号或阶段标记） |
| [qa_shot_f14_loop.png](../web/static/official/_drafts/head_only/qa_shot_f14_loop.png) | 中弹表情视觉检查帧：f14_loop（帧号或阶段标记） |
| [qa_shot_f22_outro.png](../web/static/official/_drafts/head_only/qa_shot_f22_outro.png) | 中弹表情视觉检查帧：f22_outro（帧号或阶段标记） |
| [qa_shot_f4_flash.png](../web/static/official/_drafts/head_only/qa_shot_f4_flash.png) | 中弹表情视觉检查帧：f4_flash（帧号或阶段标记） |
| [qa_shot_f7_crack.png](../web/static/official/_drafts/head_only/qa_shot_f7_crack.png) | 中弹表情视觉检查帧：f7_crack（帧号或阶段标记） |
| [qa_shot_f_last.png](../web/static/official/_drafts/head_only/qa_shot_f_last.png) | 中弹表情视觉检查帧：f_last（帧号或阶段标记） |
| [rabbit_act_head_01.jpg](../web/static/official/_drafts/head_only/rabbit_act_head_01.jpg) | “变兔子”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [rain_sad_head_01.jpg](../web/static/official/_drafts/head_only/rain_sad_head_01.jpg) | “下雨撑伞”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [shot_die_f1_smile.jpg](../web/static/official/_drafts/head_only/shot_die_f1_smile.jpg) | 中弹表情分镜：微笑起始帧 |
| [shot_die_f2_hit.jpg](../web/static/official/_drafts/head_only/shot_die_f2_hit.jpg) | 中弹表情分镜：命中反应帧 |
| [shot_die_f3_crack.jpg](../web/static/official/_drafts/head_only/shot_die_f3_crack.jpg) | 中弹表情分镜：裂纹过渡帧 |
| [shot_die_f4_xx.jpg](../web/static/official/_drafts/head_only/shot_die_f4_xx.jpg) | 中弹表情分镜：叉眼结束帧 |
| [shot_die_head_01.png](../web/static/official/_drafts/head_only/shot_die_head_01.png) | “中弹碎裂”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [shot_die_intro_00.png](../web/static/official/_drafts/head_only/shot_die_intro_00.png) | “中弹碎裂”入场过渡帧，用于表情制作，不是可直接烧录的动画包 |
| [shot_die_intro_01.png](../web/static/official/_drafts/head_only/shot_die_intro_01.png) | “中弹碎裂”入场过渡帧，用于表情制作，不是可直接烧录的动画包 |
| [shot_die_intro_02.png](../web/static/official/_drafts/head_only/shot_die_intro_02.png) | “中弹碎裂”入场过渡帧，用于表情制作，不是可直接烧录的动画包 |
| [shot_die_loop_01.png](../web/static/official/_drafts/head_only/shot_die_loop_01.png) | “中弹碎裂”循环关键帧，用于表情制作，不是可直接烧录的动画包 |
| [smile_default_head.png](../web/static/official/_drafts/head_only/smile_default_head.png) | “默认微笑”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [smile_default_head_01.png](../web/static/official/_drafts/head_only/smile_default_head_01.png) | “默认微笑”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [smug_xx_head_01.jpg](../web/static/official/_drafts/head_only/smug_xx_head_01.jpg) | “得意挑眉”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [sneeze_xx_head_01.jpg](../web/static/official/_drafts/head_only/sneeze_xx_head_01.jpg) | “打喷嚏”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [sob_flood_head_01.jpg](../web/static/official/_drafts/head_only/sob_flood_head_01.jpg) | “泪水喷涌”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [sob_flood_loop_01.png](../web/static/official/_drafts/head_only/sob_flood_loop_01.png) | “泪水喷涌”循环关键帧，用于表情制作，不是可直接烧录的动画包 |
| [soul_out_head_01.jpg](../web/static/official/_drafts/head_only/soul_out_head_01.jpg) | “灵魂出窍”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [steam_mad_head_01.jpg](../web/static/official/_drafts/head_only/steam_mad_head_01.jpg) | “冒蒸汽怒”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [sulk_act_head_01.jpg](../web/static/official/_drafts/head_only/sulk_act_head_01.jpg) | “超级委屈”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [trumpet_act_head_01.jpg](../web/static/official/_drafts/head_only/trumpet_act_head_01.jpg) | “吹喇叭”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [wink_xx_head_01.jpg](../web/static/official/_drafts/head_only/wink_xx_head_01.jpg) | “眨眼挑逗”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [yes_bounce_head_01.jpg](../web/static/official/_drafts/head_only/yes_bounce_head_01.jpg) | “大力点头”头屏关键帧，用于表情制作，不是可直接烧录的动画包 |
| [目录说明.md](../web/static/official/_drafts/head_only/%E7%9B%AE%E5%BD%95%E8%AF%B4%E6%98%8E.md) | 头屏设计草稿：文档说明 |

## web/static/official/_drafts/packer_named

带循环时间标记的候选表情 GIF

| 文件 | 用途说明 |
|---|---|
| [README.md](../web/static/official/_drafts/packer_named/README.md) | 带循环时间标记的候选表情 GIF：使用说明与当前目录文件导航 |
| [awkward_xx_[0.7s,1.7s].gif](../web/static/official/_drafts/packer_named/awkward_xx_%5B0.7s%2C1.7s%5D.gif) | “尴尬尬笑”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [bird_act_[0.8s,2.0s].gif](../web/static/official/_drafts/packer_named/bird_act_%5B0.8s%2C2.0s%5D.gif) | “变小鸟”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [bliss_bub_[0.8s,2.0s].gif](../web/static/official/_drafts/packer_named/bliss_bub_%5B0.8s%2C2.0s%5D.gif) | “幸福泡泡”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [burp_xx_[0.5s,1.4s].gif](../web/static/official/_drafts/packer_named/burp_xx_%5B0.5s%2C1.4s%5D.gif) | “打嗝”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [cat_act_[0.9s,1.9s].gif](../web/static/official/_drafts/packer_named/cat_act_%5B0.9s%2C1.9s%5D.gif) | “变小猫”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [charge_xx_[0.8s,2.0s].gif](../web/static/official/_drafts/packer_named/charge_xx_%5B0.8s%2C2.0s%5D.gif) | “充电回血”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [dog_act_[0.9s,1.9s].gif](../web/static/official/_drafts/packer_named/dog_act_%5B0.9s%2C1.9s%5D.gif) | “变小狗”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [drums_act_[0.6s,1.6s].gif](../web/static/official/_drafts/packer_named/drums_act_%5B0.6s%2C1.6s%5D.gif) | “打鼓”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [glasses_xx_[0.7s,1.7s].gif](../web/static/official/_drafts/packer_named/glasses_xx_%5B0.7s%2C1.7s%5D.gif) | “眼镜反光”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [guitar_act_[0.8s,2.0s].gif](../web/static/official/_drafts/packer_named/guitar_act_%5B0.8s%2C2.0s%5D.gif) | “弹吉他”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [heart_hands_[0.8s,1.8s].gif](../web/static/official/_drafts/packer_named/heart_hands_%5B0.8s%2C1.8s%5D.gif) | “比心”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [hello_wave_[0.7s,1.7s].gif](../web/static/official/_drafts/packer_named/hello_wave_%5B0.7s%2C1.7s%5D.gif) | “招手你好”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [idea_bulb_[0.8s,2.0s].gif](../web/static/official/_drafts/packer_named/idea_bulb_%5B0.8s%2C2.0s%5D.gif) | “灵感灯泡”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [kiss_act_[0.8s,1.8s].gif](../web/static/official/_drafts/packer_named/kiss_act_%5B0.8s%2C1.8s%5D.gif) | “飞吻”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [lightning_xx_[0.6s,1.6s].gif](../web/static/official/_drafts/packer_named/lightning_xx_%5B0.6s%2C1.6s%5D.gif) | “被雷劈”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [magic_act_[0.8s,2.0s].gif](../web/static/official/_drafts/packer_named/magic_act_%5B0.8s%2C2.0s%5D.gif) | “变魔术”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [music_25s_[0.8s,2.0s].gif](../web/static/official/_drafts/packer_named/music_25s_%5B0.8s%2C2.0s%5D.gif) | “弹钢琴”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [nap_zzz_[1.2s,2.8s].gif](../web/static/official/_drafts/packer_named/nap_zzz_%5B1.2s%2C2.8s%5D.gif) | “打瞌睡”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [no_shake_[0.6s,1.6s].gif](../web/static/official/_drafts/packer_named/no_shake_%5B0.6s%2C1.6s%5D.gif) | “摇头拒绝”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [panda_act_[0.9s,1.9s].gif](../web/static/official/_drafts/packer_named/panda_act_%5B0.9s%2C1.9s%5D.gif) | “变熊猫”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [party_xx_[0.8s,2.0s].gif](../web/static/official/_drafts/packer_named/party_xx_%5B0.8s%2C2.0s%5D.gif) | “中彩票撒花”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [rabbit_act_[0.9s,1.9s].gif](../web/static/official/_drafts/packer_named/rabbit_act_%5B0.9s%2C1.9s%5D.gif) | “变兔子”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [rain_sad_[0.9s,2.1s].gif](../web/static/official/_drafts/packer_named/rain_sad_%5B0.9s%2C2.1s%5D.gif) | “下雨撑伞”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [shot_die_[0.7s,1.7s].gif](../web/static/official/_drafts/packer_named/shot_die_%5B0.7s%2C1.7s%5D.gif) | “中弹碎裂”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [shot_die_[0.9s,1.9s].gif](../web/static/official/_drafts/packer_named/shot_die_%5B0.9s%2C1.9s%5D.gif) | “中弹碎裂”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [smug_xx_[0.8s,1.8s].gif](../web/static/official/_drafts/packer_named/smug_xx_%5B0.8s%2C1.8s%5D.gif) | “得意挑眉”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [sneeze_xx_[0.5s,1.4s].gif](../web/static/official/_drafts/packer_named/sneeze_xx_%5B0.5s%2C1.4s%5D.gif) | “打喷嚏”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [sob_flood_[1.0s,2.2s].gif](../web/static/official/_drafts/packer_named/sob_flood_%5B1.0s%2C2.2s%5D.gif) | “泪水喷涌”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [soul_out_[0.9s,2.1s].gif](../web/static/official/_drafts/packer_named/soul_out_%5B0.9s%2C2.1s%5D.gif) | “灵魂出窍”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [steam_mad_[0.5s,1.5s].gif](../web/static/official/_drafts/packer_named/steam_mad_%5B0.5s%2C1.5s%5D.gif) | “冒蒸汽怒”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [sulk_act_[0.9s,2.1s].gif](../web/static/official/_drafts/packer_named/sulk_act_%5B0.9s%2C2.1s%5D.gif) | “超级委屈”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [trumpet_act_[0.7s,1.7s].gif](../web/static/official/_drafts/packer_named/trumpet_act_%5B0.7s%2C1.7s%5D.gif) | “吹喇叭”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [yes_bounce_[0.6s,1.6s].gif](../web/static/official/_drafts/packer_named/yes_bounce_%5B0.6s%2C1.6s%5D.gif) | “大力点头”候选 GIF；文件名方括号记录循环区间，尚需打包校验 |
| [目录说明.md](../web/static/official/_drafts/packer_named/%E7%9B%AE%E5%BD%95%E8%AF%B4%E6%98%8E.md) | 打包候选素材：文档说明 |

## web/static/official/thumbs

表情资源卡片使用的 MP4 缩略预览

| 文件 | 用途说明 |
|---|---|
| [README.md](../web/static/official/thumbs/README.md) | 表情资源卡片使用的 MP4 缩略预览：使用说明与当前目录文件导航 |
| [angry_20s.mp4](../web/static/official/thumbs/angry_20s.mp4) | “生气”的 MP4 缩略预览，供网页资源卡片使用 |
| [asleep_215s.mp4](../web/static/official/thumbs/asleep_215s.mp4) | “睡着”的 MP4 缩略预览，供网页资源卡片使用 |
| [badminton_12.mp4](../web/static/official/thumbs/badminton_12.mp4) | “羽毛球”的 MP4 缩略预览，供网页资源卡片使用 |
| [confident_08.mp4](../web/static/official/thumbs/confident_08.mp4) | “自信”的 MP4 缩略预览，供网页资源卡片使用 |
| [cry_10s_10s.mp4](../web/static/official/thumbs/cry_10s_10s.mp4) | “哭泣”的 MP4 缩略预览，供网页资源卡片使用 |
| [investigate_.mp4](../web/static/official/thumbs/investigate_.mp4) | “观察”的 MP4 缩略预览，供网页资源卡片使用 |
| [laugh_05s_10.mp4](../web/static/official/thumbs/laugh_05s_10.mp4) | “大笑”的 MP4 缩略预览，供网页资源卡片使用 |
| [leisure_05s_.mp4](../web/static/official/thumbs/leisure_05s_.mp4) | “悠闲”的 MP4 缩略预览，供网页资源卡片使用 |
| [mock_05s.mp4](../web/static/official/thumbs/mock_05s.mp4) | “调皮”的 MP4 缩略预览，供网页资源卡片使用 |
| [mute_05s.mp4](../web/static/official/thumbs/mute_05s.mp4) | “无语”的 MP4 缩略预览，供网页资源卡片使用 |
| [panic_05s_15.mp4](../web/static/official/thumbs/panic_05s_15.mp4) | “慌张”的 MP4 缩略预览，供网页资源卡片使用 |
| [ponder_05s.mp4](../web/static/official/thumbs/ponder_05s.mp4) | “思考”的 MP4 缩略预览，供网页资源卡片使用 |
| [question_05s.mp4](../web/static/official/thumbs/question_05s.mp4) | “疑问”的 MP4 缩略预览，供网页资源卡片使用 |
| [sad_05s15s.mp4](../web/static/official/thumbs/sad_05s15s.mp4) | “难过”的 MP4 缩略预览，供网页资源卡片使用 |
| [shocked_05s_.mp4](../web/static/official/thumbs/shocked_05s_.mp4) | “震惊”的 MP4 缩略预览，供网页资源卡片使用 |
| [shy_20s_40s.mp4](../web/static/official/thumbs/shy_20s_40s.mp4) | “害羞”的 MP4 缩略预览，供网页资源卡片使用 |
| [sigh_20s_20s.mp4](../web/static/official/thumbs/sigh_20s_20s.mp4) | “叹气”的 MP4 缩略预览，供网页资源卡片使用 |
| [smile_05s.mp4](../web/static/official/thumbs/smile_05s.mp4) | “微笑”的 MP4 缩略预览，供网页资源卡片使用 |
| [smile_static.mp4](../web/static/official/thumbs/smile_static.mp4) | “静态微笑”的 MP4 缩略预览，供网页资源卡片使用 |
| [snigger_10s.mp4](../web/static/official/thumbs/snigger_10s.mp4) | “窃笑”的 MP4 缩略预览，供网页资源卡片使用 |
| [yawn_20s.mp4](../web/static/official/thumbs/yawn_20s.mp4) | “哈欠”的 MP4 缩略预览，供网页资源卡片使用 |
| [yummy_20_s.mp4](../web/static/official/thumbs/yummy_20_s.mp4) | “美味”的 MP4 缩略预览，供网页资源卡片使用 |

## web/tests

网页交互、协议、资源管理和识别接入测试

| 文件 | 用途说明 |
|---|---|
| [README.md](../web/tests/README.md) | 网页交互、协议、资源管理和识别接入测试：使用说明与当前目录文件导航 |
| [test_ble_recovery.py](../web/tests/test_ble_recovery.py) | 蓝牙断线、重连与错误处理测试 |
| [test_composer_store.py](../web/tests/test_composer_store.py) | 组合存储、声音上传、合成、资源引用和表情循环参数测试 |
| [test_composer_timeline.cjs](../web/tests/test_composer_timeline.cjs) | 时间轴片段吸附、位置冲突与移动规则测试 |
| [test_composition_runner_sync.py](../web/tests/test_composition_runner_sync.py) | 组合动作、表情与声音调度同步测试 |
| [test_controls.cjs](../web/tests/test_controls.cjs) | 单次/连续动作按钮、状态恢复与停止切换测试 |
| [test_expression_loop.cjs](../web/tests/test_expression_loop.cjs) | 表情循环时间及自定义表情元数据测试 |
| [test_motion_tempo.cjs](../web/tests/test_motion_tempo.cjs) | 动作节奏变体、默认节奏及前端选择控件测试 |
| [test_portable_runtime.py](../web/tests/test_portable_runtime.py) | 仓库相对路径、配置覆盖及非默认端口请求校验测试 |
| [test_programs.py](../web/tests/test_programs.py) | 动作程序、角度边界、时长、协议容量、设备身份与表情预览测试 |
| [test_release_models.py](../web/tests/test_release_models.py) | 发布模型包校验、按类型解压及路径越界拒绝测试 |
| [test_video_input.py](../web/tests/test_video_input.py) | 网页视频帧会话、识别结果与控制接入测试 |
| [test_voice_trigger.py](../web/tests/test_voice_trigger.py) | 语音输入、唤醒词、关键词触发和识别模型接入测试 |

