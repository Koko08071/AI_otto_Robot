# 维护与发布

1. 修改动作或手势映射后，运行 `gesture_recognition` 和 `web/tests` 中的自动化测试。
2. 检查 `git diff`，确认没有 Wi-Fi 密码、API Token、模型权重、语音模型和刷机产物。
3. 前端修改后运行 `node --check web/static/app.js` 和 `node --check web/static/composer.js`。
4. 先在本地网页控制台验证，再提交 Git。
5. 固件刷写前确认芯片序列号和目标设备，默认不擦除 NVS。

公开仓库只保存可复现的源码、资源索引和文档；设备专属配置放在本地 `.env` 或未提交的 ESP-IDF 配置中。
