#pragma once

#include "esp_err.h"

namespace otto { class Robot; }

namespace otto_wifi {

esp_err_t start(otto::Robot *robot);

}
