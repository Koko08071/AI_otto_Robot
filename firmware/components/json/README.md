# JSON 组件兼容层

通过 CMake 将旧组件名 json 依赖转接到 espressif__cjson，供 esp_emote_gen_player 在 ESP-IDF 6.1 下使用。

此处不是动作配置文件；动作数据在 ../../../web/static/actions.json。

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [CMakeLists.txt](CMakeLists.txt) | 将 json 组件依赖转接给 espressif__cjson |
| [README.md](README.md) | 旧 json 组件名到 espressif__cjson 的兼容层：使用说明与当前目录文件导航 |
<!-- FILE-INDEX:END -->
