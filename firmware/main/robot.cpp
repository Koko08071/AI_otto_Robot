#include "robot.hpp"

#include "esp_log.h"
#include "esp_spiffs.h"
#include "nvs_flash.h"
#include "sdkconfig.h"

namespace otto {
namespace {
constexpr auto kTag = "robot";
}

esp_err_t Robot::init() {
    esp_err_t result = nvs_flash_init();
    if (result == ESP_ERR_NVS_NO_FREE_PAGES || result == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_LOGE(kTag, "NVS incompatible; refusing to erase existing settings");
        return result;
    }
    if (result != ESP_OK) return result;

    esp_vfs_spiffs_conf_t storage = {};
    storage.base_path = "/spiffs";
    storage.partition_label = "storage";
    storage.max_files = 8;
    storage.format_if_mount_failed = false;
    result = esp_vfs_spiffs_register(&storage);
    if (result != ESP_OK) {
        ESP_LOGE(kTag, "Behavior storage unavailable: %s", esp_err_to_name(result));
        return result;
    }

    const BoardProfile profile = board_profile();
    if (profile.valid) {
        result = display_.init(profile);
        if (result != ESP_OK) return result;
    } else {
        ESP_LOGW(kTag, "No board profile selected; this image is a safe offline build");
    }
    result = face_.init(&display_);
    if (result != ESP_OK) return result;
    result = face_.load_assets(nullptr);
    if (result != ESP_OK) return result;
#if defined(CONFIG_OTTO_SERVO_OUTPUT_ENABLE)
    constexpr bool allow_servo_output = true;
#else
    constexpr bool allow_servo_output = false;
#endif
    result = motion_.init(profile, allow_servo_output);
    if (result != ESP_OK) return result;
    result = behavior_.init(&motion_, &face_);
    if (result == ESP_OK) ESP_LOGI(kTag, "Robot ready: board=%s servo_output=%d", profile.name,
                                  motion_.output_enabled());
    return result;
}

bool Robot::play_json(const std::string &json, Priority priority) { return behavior_.play_json(json, priority); }
bool Robot::move_pose(const Pose &pose, uint32_t duration_ms) {
    return behavior_.move_pose(pose, duration_ms);
}

void Robot::home() { behavior_.home(); }
void Robot::stop() { behavior_.stop(); }
void Robot::emergency_detach() { behavior_.cancel(); motion_.detach(); }

} // namespace otto
