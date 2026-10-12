# 维护与发布

1. 修改动作或手势映射后，运行 `gesture_recognition` 和 `web/tests` 中的自动化测试。
2. 检查 `git diff`，确认没有 Wi-Fi 密码、API Token 或设备 NVS 备份；模型和运行环境通过 Releases 发布，公开刷机镜像须使用占位网络配置并附校验清单。
3. 前端修改后运行 `node --check web/static/app.js` 和 `node --check web/static/composer.js`。
4. 先在本地网页控制台验证，再提交 Git。
5. 固件刷写前确认芯片序列号和目标设备，默认不擦除 NVS。

公开仓库包含源码、文档、演示音频和公开刷机资源；模型与完整 Windows 运行包放在 GitHub Releases，下载链接和校验值见 `release-assets.json`。电脑端设备配置放在本地 `config.local.json`（从 `config.example.json` 复制），私人固件配置不提交。同名环境变量优先，代码不自动读取 `.env`。
