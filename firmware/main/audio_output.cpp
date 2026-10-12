#include "audio_output.hpp"
#include "driver/i2s_std.h"
#include "freertos/FreeRTOS.h"
#include "sdkconfig.h"
#include <array>
#include <atomic>

namespace otto_audio {
namespace {
i2s_chan_handle_t tx = nullptr;
std::atomic<unsigned> generation{0};
}

esp_err_t init() {
#if CONFIG_OTTO_BOARD_NO_CAMERA
    i2s_chan_config_t channel = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    channel.dma_desc_num = 6;
    channel.dma_frame_num = 240;
    esp_err_t err = i2s_new_channel(&channel, &tx, nullptr);
    if (err != ESP_OK) return err;
    i2s_std_config_t config = {};
    config.clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(24000);
    config.slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO);
    config.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;
    config.gpio_cfg.mclk = I2S_GPIO_UNUSED;
    config.gpio_cfg.bclk = GPIO_NUM_15;
    config.gpio_cfg.ws = GPIO_NUM_16;
    config.gpio_cfg.dout = GPIO_NUM_7;
    config.gpio_cfg.din = I2S_GPIO_UNUSED;
    err = i2s_channel_init_std_mode(tx, &config);
    if (err != ESP_OK) { i2s_del_channel(tx); tx = nullptr; }
    return err;
#else
    return ESP_OK;
#endif
}

bool available() { return tx != nullptr; }
void stop() { ++generation; }

esp_err_t write_pcm16(const int16_t *samples, size_t count) {
    if (!tx) return ESP_ERR_NOT_SUPPORTED;
    esp_err_t result = i2s_channel_enable(tx);
    if (result != ESP_OK) return result;
    const unsigned started=generation.load();
    std::array<int32_t, 1024> expanded;
    while (count) {
        if (started!=generation.load()) break;
        const size_t chunk = count < expanded.size() ? count : expanded.size();
        for (size_t i=0;i<chunk;++i) expanded[i] = int32_t(samples[i]) * 65536;
        size_t written = 0;
        const esp_err_t err = i2s_channel_write(tx, expanded.data(), chunk*sizeof(int32_t), &written, portMAX_DELAY);
        if (err != ESP_OK || written != chunk*sizeof(int32_t)) {
            result = err == ESP_OK ? ESP_FAIL : err;
            break;
        }
        samples += chunk;
        count -= chunk;
    }
    expanded.fill(0);
    size_t written = 0;
    i2s_channel_write(tx, expanded.data(), expanded.size()*sizeof(int32_t), &written, pdMS_TO_TICKS(100));
    vTaskDelay(pdMS_TO_TICKS(60));
    i2s_channel_disable(tx);
    return result;
}
}
