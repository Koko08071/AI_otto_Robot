# 网页与多轨编排器

网页控制台资源位于 `web/static/`。多轨编排器支持动作、表情、声音三类轨道，以及拖拽、吸附、复制粘贴、屏蔽、保存组合和机器人执行。

组合保存到 `web/library/compositions/`。声音文件属于本机生成资源，不建议提交到公开仓库；目录已加入 `.gitignore`。

动作目录是 `web/static/actions.json`，表情目录是 `web/static/expressions.json`。新增表情要同时确认固件资源和资源 ID 已存在。
