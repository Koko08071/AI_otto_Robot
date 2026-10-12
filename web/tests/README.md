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
