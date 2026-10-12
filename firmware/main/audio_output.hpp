#pragma once
#include "esp_err.h"
#include <cstddef>
#include <cstdint>

namespace otto_audio {
esp_err_t init();
bool available();
void stop();
esp_err_t write_pcm16(const int16_t *samples, size_t count);
}
