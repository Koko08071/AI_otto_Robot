#include "board_display.hpp"

#include <cstring>
#include <algorithm>
#include "driver/ledc.h"
#include "driver/spi_master.h"
#include "esp_check.h"
#include "esp_heap_caps.h"
#include "esp_lcd_panel_vendor.h"
#include "esp_log.h"
#if defined(CONFIG_OTTO_EMOTE_GEN_PLAYER)
#include "emote_gen_player.h"
#endif

namespace otto {
namespace {
constexpr int kStripRows = 48;
constexpr int kControllerRows = 320;
constexpr int kViewportY = (kControllerRows - BoardDisplay::kHeight) / 2;
constexpr auto kTag = "board_display";
}

bool BoardDisplay::transfer_done(esp_lcd_panel_io_handle_t, esp_lcd_panel_io_event_data_t *, void *ctx) {
    auto *self = static_cast<BoardDisplay *>(ctx);
    BaseType_t awakened = pdFALSE;
    xSemaphoreGiveFromISR(self->transfer_sem_, &awakened);
    return awakened == pdTRUE;
}

esp_err_t BoardDisplay::submit_region(int x0, int y0, int x1, int y1, const void *rgb565) {
    if (!panel_ || !rgb565 || x0 < 0 || y0 < 0 || x1 > kAnimationSize || y1 > kAnimationSize || x0 >= x1 || y0 >= y1)
        return ESP_ERR_INVALID_ARG;
    // Composite dirty animation strips into a persistent screen buffer. Source assets
    // stay unchanged: 360 -> 240 nearest-neighbour, then 90 degrees counterclockwise.
    const int left = (x0 * 2 + 2) / 3, right = (x1 * 2 + 2) / 3;
    const int top = (y0 * 2 + 2) / 3, bottom = (y1 * 2 + 2) / 3;
    const auto *pixels = static_cast<const uint16_t *>(rgb565);
    for (int y=top; y<bottom; ++y)
        for (int x=left; x<right; ++x)
            framebuffer_[(kWidth-1-x)*kWidth+y] = pixels[(y*3/2-y0)*(x1-x0)+(x*3/2-x0)];

    return ESP_OK;
}

esp_err_t BoardDisplay::init(const BoardProfile &profile) {
    if (!profile.valid) {
        ESP_LOGW(kTag, "Board profile disabled; display output remains off");
        return ESP_ERR_INVALID_STATE;
    }
    backlight_pin_ = profile.backlight;
    transfer_sem_ = xSemaphoreCreateBinary();
    dma_strip_ = static_cast<uint16_t *>(heap_caps_malloc(kWidth * kStripRows * sizeof(uint16_t),
                                                           MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL));
    framebuffer_=static_cast<uint16_t *>(heap_caps_calloc(kWidth*kHeight,sizeof(uint16_t),MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
    if (!transfer_sem_ || !dma_strip_ || !framebuffer_) return ESP_ERR_NO_MEM;

    spi_bus_config_t bus = {};
    bus.mosi_io_num = profile.lcd_mosi;
    bus.miso_io_num = GPIO_NUM_NC;
    bus.sclk_io_num = profile.lcd_clk;
    bus.quadwp_io_num = GPIO_NUM_NC;
    bus.quadhd_io_num = GPIO_NUM_NC;
    bus.max_transfer_sz = kWidth * kStripRows * sizeof(uint16_t);
    ESP_RETURN_ON_ERROR(spi_bus_initialize(SPI3_HOST, &bus, SPI_DMA_CH_AUTO), kTag, "SPI3 init failed");

    esp_lcd_panel_io_spi_config_t io = {};
    io.cs_gpio_num = profile.lcd_cs;
    io.dc_gpio_num = profile.lcd_dc;
    io.spi_mode = 3;
    io.pclk_hz = 40 * 1000 * 1000;
    io.trans_queue_depth = 1;
    io.lcd_cmd_bits = 8;
    io.lcd_param_bits = 8;
    io.on_color_trans_done = transfer_done;
    io.user_ctx = this;
    ESP_RETURN_ON_ERROR(esp_lcd_new_panel_io_spi(SPI3_HOST, &io, &panel_io_), kTag, "panel IO failed");

    esp_lcd_panel_dev_config_t panel_config = {};
    panel_config.reset_gpio_num = profile.lcd_rst;
    panel_config.rgb_ele_order = LCD_RGB_ELEMENT_ORDER_RGB;
    panel_config.bits_per_pixel = 16;
    ESP_RETURN_ON_ERROR(esp_lcd_new_panel_st7789(panel_io_, &panel_config, &panel_), kTag, "ST7789 failed");
    ESP_RETURN_ON_ERROR(esp_lcd_panel_reset(panel_), kTag, "panel reset failed");
    ESP_RETURN_ON_ERROR(esp_lcd_panel_init(panel_), kTag, "panel init failed");
    ESP_RETURN_ON_ERROR(esp_lcd_panel_invert_color(panel_, true), kTag, "inversion failed");
    ESP_RETURN_ON_ERROR(esp_lcd_panel_swap_xy(panel_, false), kTag, "axis setup failed");
    ESP_RETURN_ON_ERROR(esp_lcd_panel_mirror(panel_, false, false), kTag, "mirror setup failed");
    ESP_RETURN_ON_ERROR(esp_lcd_panel_disp_on_off(panel_, true), kTag, "display enable failed");

    ledc_timer_config_t timer = {};
    timer.speed_mode = LEDC_LOW_SPEED_MODE;
    timer.duty_resolution = LEDC_TIMER_10_BIT;
    timer.timer_num = LEDC_TIMER_0;
    timer.freq_hz = 5000;
    timer.clk_cfg = LEDC_AUTO_CLK;
    ESP_RETURN_ON_ERROR(ledc_timer_config(&timer), kTag, "backlight timer failed");
    ledc_channel_config_t channel = {};
    channel.gpio_num = backlight_pin_;
    channel.speed_mode = LEDC_LOW_SPEED_MODE;
    channel.channel = LEDC_CHANNEL_4;
    channel.timer_sel = LEDC_TIMER_0;
    channel.intr_type = LEDC_INTR_DISABLE;
    channel.duty = 0;
    ESP_RETURN_ON_ERROR(ledc_channel_config(&channel), kTag, "backlight channel failed");
    ESP_RETURN_ON_ERROR(clear(),kTag,"initial screen clear failed");
    return set_backlight(70);
}

esp_err_t BoardDisplay::clear() {
    if (!framebuffer_) return ESP_ERR_INVALID_STATE;
    std::memset(framebuffer_,0,kWidth*kHeight*sizeof(uint16_t));
    // ST7789 has 240x320 addressable GRAM, even on modules with a smaller
    // visible window. Clear the controller, not just our animation viewport.
    std::memset(dma_strip_,0,kWidth*kStripRows*sizeof(uint16_t));
    for (int y=0;y<kControllerRows;y+=kStripRows) {
        const int rows=std::min(kStripRows,kControllerRows-y);
        ESP_RETURN_ON_ERROR(esp_lcd_panel_draw_bitmap(panel_,0,y,kWidth,y+rows,dma_strip_),kTag,"full GRAM clear failed");
        if (xSemaphoreTake(transfer_sem_,pdMS_TO_TICKS(200))!=pdTRUE) return ESP_ERR_TIMEOUT;
    }
    return ESP_OK;
}

esp_err_t BoardDisplay::flush_frame() {
    if (!panel_ || !framebuffer_) return ESP_ERR_INVALID_STATE;
    for (int y=0;y<kHeight;y+=kStripRows) {
        const int rows=std::min(kStripRows,kHeight-y);
        // gfx supplies panel-order RGB565 bytes; do not swap them a second time.
        std::memcpy(dma_strip_,framebuffer_+y*kWidth,kWidth*rows*sizeof(uint16_t));
        ESP_RETURN_ON_ERROR(esp_lcd_panel_draw_bitmap(panel_,0,y+kViewportY,kWidth,y+rows+kViewportY,dma_strip_),kTag,"draw failed");
        if (xSemaphoreTake(transfer_sem_,pdMS_TO_TICKS(200))!=pdTRUE) return ESP_ERR_TIMEOUT;
    }
    return ESP_OK;
}

esp_err_t BoardDisplay::set_backlight(uint8_t percent) {
    if (backlight_pin_ == GPIO_NUM_NC || percent > 100) return ESP_ERR_INVALID_ARG;
    const uint32_t duty = 1023U * percent / 100U;
    ESP_RETURN_ON_ERROR(ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_4, duty), kTag, "duty failed");
    return ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_4);
}

esp_err_t BoardDisplay::set_enabled(bool enabled) {
    if (!panel_) return ESP_ERR_INVALID_STATE;
    return esp_lcd_panel_disp_on_off(panel_, enabled);
}

} // namespace otto
