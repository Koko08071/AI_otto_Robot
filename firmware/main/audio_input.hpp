#pragma once
#include <cstddef>
#include <cstdint>
#include "esp_err.h"

namespace otto_mic {
esp_err_t init();
bool available();
esp_err_t read_pcm16(int16_t *samples, size_t count);
}
