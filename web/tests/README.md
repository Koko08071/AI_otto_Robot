# 网页与服务端测试

- test_programs.py：动作参数与协议校验。
- test_composer_store.py：组合保存与资源管理。
- test_composition_runner_sync.py：组合执行时序。
- test_voice_trigger.py / test_video_input.py：语音、视频输入逻辑。
- test_ble_recovery.py：蓝牙恢复逻辑。
- *.cjs：前端控制、时间线、表情循环和节奏测试。

Python 测试从仓库根目录执行 python -m unittest discover -s web/tests。
JavaScript 测试使用 node --test web/tests/*.cjs。
部分测试依赖 FFmpeg、平台语音合成或未随包提供的历史资源，详见具体用例。

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [README.md](README.md) | 网页交互、协议、资源管理和识别接入测试：使用说明与当前目录文件导航 |
| [test_ble_recovery.py](test_ble_recovery.py) | 蓝牙断线、重连与错误处理测试 |
| [test_composer_store.py](test_composer_store.py) | 组合存储、声音上传、合成、资源引用和表情循环参数测试 |
| [test_composer_timeline.cjs](test_composer_timeline.cjs) | 时间轴片段吸附、位置冲突与移动规则测试 |
| [test_composition_runner_sync.py](test_composition_runner_sync.py) | 组合动作、表情与声音调度同步测试 |
| [test_controls.cjs](test_controls.cjs) | 单次/连续动作按钮、状态恢复与停止切换测试 |
| [test_expression_loop.cjs](test_expression_loop.cjs) | 表情循环时间及自定义表情元数据测试 |
| [test_motion_tempo.cjs](test_motion_tempo.cjs) | 动作节奏变体、默认节奏及前端选择控件测试 |
| [test_portable_runtime.py](test_portable_runtime.py) | 仓库相对路径、配置覆盖及非默认端口请求校验测试 |
| [test_programs.py](test_programs.py) | 动作程序、角度边界、时长、协议容量、设备身份与表情预览测试 |
| [test_video_input.py](test_video_input.py) | 网页视频帧会话、识别结果与控制接入测试 |
| [test_voice_trigger.py](test_voice_trigger.py) | 语音输入、唤醒词、关键词触发和识别模型接入测试 |
<!-- FILE-INDEX:END -->
