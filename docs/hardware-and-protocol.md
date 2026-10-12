# 硬件与通信

## 舵机通道

数组顺序固定为 `[左腿, 右腿, 左脚, 右脚]`。

| 通道 | 部位 | GPIO |
|---|---|---:|
| `ll` | 左腿 | 39 |
| `rl` | 右腿 | 17 |
| `lf` | 左脚 | 38 |
| `rf` | 右脚 | 18 |

## 无线接口

- Wi-Fi：HTTP API，网页服务通过 `OTTO_DEVICE_URL` 连接。
- BLE：由网页本地 Python 服务扫描和转发控制指令。
- USB：主要用于 ESP32-S3 刷机和串口诊断，不是实时控制必需连接。

## 常用接口

- `GET /api/status`
- `POST /api/play`
- `POST /api/stop`
- `POST /api/home`
- `POST /api/face`
- `POST /api/output`

角度范围为 `0-180` 度。没有舵机位置传感器，状态回读代表固件最后下发的目标角度，不等于机械实际角度。
