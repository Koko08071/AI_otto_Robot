#pragma once

#include <cstdint>
#include "board_profile.hpp"
#include "esp_err.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

namespace otto {

class BoardDisplay {
public:
    static constexpr int kWidth = 240;
    static constexpr int kHeight = 240;
    static constexpr int kAnimationSize = 360;

    esp_err_t init(const BoardProfile &profile);
    esp_err_t clear();
    esp_err_t flush_frame();
    esp_err_t submit_region(int x0, int y0, int x1, int y1, const void *rgb565);
    esp_err_t set_backlight(uint8_t percent);
    esp_err_t set_enabled(bool enabled);
    bool available() const { return panel_ != nullptr; }

private:
    static bool transfer_done(esp_lcd_panel_io_handle_t, esp_lcd_panel_io_event_data_t *, void *ctx);

    esp_lcd_panel_io_handle_t panel_io_ = nullptr;
    esp_lcd_panel_handle_t panel_ = nullptr;
    SemaphoreHandle_t transfer_sem_ = nullptr;
    uint16_t *dma_strip_ = nullptr;
    uint16_t *framebuffer_ = nullptr;
    gpio_num_t backlight_pin_ = GPIO_NUM_NC;
};

} // namespace otto
