#include "audio_input.hpp"
#include "driver/i2s_std.h"
#include "freertos/FreeRTOS.h"
#include "sdkconfig.h"
#include <array>
#include <algorithm>

namespace otto_mic {
namespace { i2s_chan_handle_t rx = nullptr; }

esp_err_t init() {
#if CONFIG_OTTO_BOARD_NO_CAMERA
    // Original no-camera Otto firmware: I2S1, 16 kHz, 32-bit left slot,
    // microphone SCK=5, WS=4, DIN=6.
    i2s_chan_config_t channel = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_1, I2S_ROLE_MASTER);
    channel.dma_desc_num = 6;
    channel.dma_frame_num = 256;
    esp_err_t err = i2s_new_channel(&channel, nullptr, &rx);
    if (err != ESP_OK) return err;
    i2s_std_config_t config = {};
    config.clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(16000);
    config.slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO);
    config.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;
    config.gpio_cfg.mclk = I2S_GPIO_UNUSED;
    config.gpio_cfg.bclk = GPIO_NUM_5;
    config.gpio_cfg.ws = GPIO_NUM_4;
    config.gpio_cfg.dout = I2S_GPIO_UNUSED;
    config.gpio_cfg.din = GPIO_NUM_6;
    err = i2s_channel_init_std_mode(rx, &config);
    if (err == ESP_OK) err = i2s_channel_enable(rx);
    if (err != ESP_OK) { i2s_del_channel(rx); rx = nullptr; }
    return err;
#else
    return ESP_OK;
#endif
}

bool available() { return rx != nullptr; }

esp_err_t read_pcm16(int16_t *samples, size_t count) {
    if (!rx) return ESP_ERR_NOT_SUPPORTED;
    std::array<int32_t, 512> raw;
    while (count) {
        const size_t chunk = std::min(count, raw.size());
        const size_t wanted = chunk * sizeof(int32_t);
        size_t bytes = 0;
        while (bytes < wanted) {
            size_t received = 0;
            const esp_err_t err = i2s_channel_read(rx, reinterpret_cast<uint8_t *>(raw.data()) + bytes,
                                                   wanted - bytes, &received, portMAX_DELAY);
            if (err != ESP_OK || !received) return err == ESP_OK ? ESP_FAIL : err;
            bytes += received;
        }
        for (size_t i = 0; i < chunk; ++i) {
            const int32_t sample = raw[i] >> 12; // Match original NoAudioCodec::Read.
            samples[i] = static_cast<int16_t>(std::clamp(sample, int32_t(-32768), int32_t(32767)));
        }
        samples += chunk;
        count -= chunk;
    }
    return ESP_OK;
}
}
