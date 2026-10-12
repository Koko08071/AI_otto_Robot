#pragma once

#include <array>
#include "driver/gpio.h"
#include "sdkconfig.h"

namespace otto {

struct BoardProfile {
    const char *name;
    bool valid;
    std::array<gpio_num_t, 4> servo_pins; // LL, RL, LF, RF
    gpio_num_t lcd_mosi;
    gpio_num_t lcd_clk;
    gpio_num_t lcd_dc;
    gpio_num_t lcd_rst;
    gpio_num_t lcd_cs;
    gpio_num_t backlight;
};

constexpr BoardProfile board_profile() {
#if CONFIG_OTTO_BOARD_CAMERA
    // Motion order is LL, RL, physical left foot (firmware rf), physical right foot (firmware lf).
    return {"camera-candidate", true, {GPIO_NUM_5, GPIO_NUM_43, GPIO_NUM_44, GPIO_NUM_6},
            GPIO_NUM_45, GPIO_NUM_48, GPIO_NUM_47, GPIO_NUM_1, GPIO_NUM_NC, GPIO_NUM_38};
#elif CONFIG_OTTO_BOARD_NO_CAMERA
    // Confirmed on this robot: robot-relative LL=39, RL=17, LF=38, RF=18.
    return {"no-camera-verified", true, {GPIO_NUM_39, GPIO_NUM_17, GPIO_NUM_38, GPIO_NUM_18},
            GPIO_NUM_10, GPIO_NUM_9, GPIO_NUM_46, GPIO_NUM_11, GPIO_NUM_12, GPIO_NUM_3};
#else
    return {"disabled", false, {GPIO_NUM_NC, GPIO_NUM_NC, GPIO_NUM_NC, GPIO_NUM_NC},
            GPIO_NUM_NC, GPIO_NUM_NC, GPIO_NUM_NC, GPIO_NUM_NC, GPIO_NUM_NC, GPIO_NUM_NC};
#endif
}

} // namespace otto
