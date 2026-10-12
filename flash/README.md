# 公开刷机文件：ESP32-S3 无摄像头 Otto

本目录用于空白主板复刻或固件恢复。已有兼容固件的机器人只需启动电脑控制台，不需要重新刷机。

## 对应硬件

- ESP32-S3，16 MB Flash、Octal PSRAM；无摄像头主板。
- 四舵机顺序：左腿 GPIO39、右腿 GPIO17、左脚 GPIO38、右脚 GPIO18。
- ST7789 屏幕及 I2S 音频，引脚定义见 `firmware/main/board_profile.hpp`。
- 不可直接套用于不同主板、不同 Flash/PSRAM 规格或不同引脚。

## 文件与地址

| 写入地址 | 文件 | 用途 |
|---|---|---|
| `0x0` | `bootloader.bin` | 启动引导程序 |
| `0x8000` | `partition-table.bin` | Flash 分区表 |
| `0x20000` | `otto_expression_motion.bin` | 公开配置重新构建的主程序 |
| `0x700000` | `storage.bin` | SPIFFS 存储分区 |
| `0x800000` | `all_emote_assets.bin` | 官方精简表情与 32 个头屏表情资源 |

`manifest.json` 记录文件 SHA256、构建来源和验证范围。这里不提供设备 NVS 备份，也不包含私人 Wi-Fi 密码。

## 连接限制

公开固件使用 `YOUR_WIFI_SSID` / `YOUR_WIFI_PASSWORD` 等占位配置。刷入后可以先使用蓝牙 `Otto-0E70` 进行控制；Wi-Fi、机身音频需要先用自己的网络参数重新构建固件。当前固件没有面向最终用户的 Wi-Fi 配网向导。

控制台 `config.local.json` 中的设备 ID 要与实际芯片 MAC 一致；修改电脑上的 IP 配置不会替机器人配网。

## 手工刷写

以下操作只适用于已经核实的主板。断开舵机电源或使机身处于不会跌落的位置，先确定下载模式和实际串口。命令中的 `COM3` 仅是示例。

```powershell
.\runtime\python.exe -m esptool --chip esp32s3 --port COM3 chip_id
.\runtime\python.exe -m esptool --chip esp32s3 --port COM3 write_flash --flash_size 16MB 0x0 flash/bootloader.bin 0x8000 flash/partition-table.bin 0x20000 flash/otto_expression_motion.bin 0x700000 flash/storage.bin 0x800000 flash/all_emote_assets.bin
```

源码安装方式可改用 `.venv/Scripts/python.exe`。不要先执行 erase_flash：以上映射不主动覆盖 NVS，但写入固件仍会改变设备行为。公开固件仅完成构建和镜像校验，没有为本次发布刷入实机验证。

<!-- FILE-INDEX:START -->
## 当前目录逐项说明

| 文件或子目录 | 用途说明 |
|---|---|
| [README.md](README.md) | 公开刷机文件、写入地址与镜像校验信息：使用说明与当前目录文件导航 |
| [all_emote_assets.bin](all_emote_assets.bin) | 官方精简及 32 个头屏表情分区镜像，写入 0x800000 |
| [bootloader.bin](bootloader.bin) | 公开固件引导程序，写入 0x0 |
| [manifest.json](manifest.json) | 公开固件构建来源、写入地址和每个镜像的 SHA256 |
| [otto_expression_motion.bin](otto_expression_motion.bin) | 不含私人网络配置的公开主程序，写入 0x20000 |
| [partition-table.bin](partition-table.bin) | 16 MB Flash 分区表，写入 0x8000 |
| [storage.bin](storage.bin) | storage SPIFFS 分区镜像，写入 0x700000 |
<!-- FILE-INDEX:END -->
