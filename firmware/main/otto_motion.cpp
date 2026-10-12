#include "otto_motion.hpp"

#include <algorithm>
#include <cmath>
#include <cstring>
#include "driver/ledc.h"
#include "esp_check.h"
#include "esp_log.h"
#include "nvs.h"

namespace otto {
namespace {
constexpr auto kTag = "otto_motion";
constexpr uint32_t kPwmHz = 50;
constexpr uint32_t kDutyResolution = 8192;
constexpr float kMinPulseUs = 500.0f;
constexpr float kMaxPulseUs = 2500.0f;
constexpr ledc_channel_t kChannels[] = {LEDC_CHANNEL_0, LEDC_CHANNEL_1, LEDC_CHANNEL_2, LEDC_CHANNEL_3};
constexpr const char *kNvsKeys[] = {"left_leg", "right_leg", "left_foot", "right_foot"};

float clamp_angle(float value) { return std::clamp(value, 0.0f, 180.0f); }
}

bool OttoMotion::valid_calibration(const ServoCalibration &value) {
    return std::isfinite(value.neutral) && std::isfinite(value.trim) &&
           std::isfinite(value.minimum) && std::isfinite(value.maximum) &&
           (value.direction == 1 || value.direction == -1) && value.minimum >= 0 &&
           value.maximum <= 180 && value.minimum <= value.neutral &&
           value.neutral <= value.maximum && std::abs(value.trim) <= 50;
}

void OttoMotion::load_calibration() {
    nvs_handle_t handle;
    if (nvs_open("otto_motion", NVS_READONLY, &handle) != ESP_OK) return;
    for (size_t i = 0; i < calibration_.size(); ++i) {
        ServoCalibration loaded{};
        size_t length = sizeof(loaded);
        if (nvs_get_blob(handle, kNvsKeys[i], &loaded, &length) == ESP_OK &&
            length == sizeof(loaded) && valid_calibration(loaded)) {
            calibration_[i] = loaded;
        }
    }
    nvs_close(handle);
}

esp_err_t OttoMotion::init(const BoardProfile &profile, bool allow_output) {
    load_calibration();
    if (!profile.valid || !allow_output) {
        ESP_LOGW(kTag, "Servo PWM disabled: board=%s allow_output=%d", profile.name, allow_output);
        return ESP_OK;
    }
    ledc_timer_config_t timer = {};
    timer.speed_mode = LEDC_LOW_SPEED_MODE;
    timer.timer_num = LEDC_TIMER_1;
    timer.duty_resolution = LEDC_TIMER_13_BIT;
    timer.freq_hz = kPwmHz;
    timer.clk_cfg = LEDC_AUTO_CLK;
    ESP_RETURN_ON_ERROR(ledc_timer_config(&timer), kTag, "servo timer failed");
    for (size_t i = 0; i < profile.servo_pins.size(); ++i) {
        ledc_channel_config_t channel = {};
        channel.gpio_num = profile.servo_pins[i];
        channel.speed_mode = LEDC_LOW_SPEED_MODE;
        channel.channel = kChannels[i];
        channel.intr_type = LEDC_INTR_DISABLE;
        channel.timer_sel = LEDC_TIMER_1;
        channel.duty = 0;
        ESP_RETURN_ON_ERROR(ledc_channel_config(&channel), kTag, "servo channel %u failed", unsigned(i));
    }
    output_available_ = true;
    // Wait for an explicit enable command before applying servo power pulses.
    return ESP_OK;
}

esp_err_t OttoMotion::set_calibration(Servo servo, const ServoCalibration &value, bool persist) {
    const size_t index = static_cast<size_t>(servo);
    if (index >= calibration_.size() || !valid_calibration(value)) return ESP_ERR_INVALID_ARG;
    if (persist) {
        nvs_handle_t handle;
        ESP_RETURN_ON_ERROR(nvs_open("otto_motion", NVS_READWRITE, &handle), kTag, "NVS open failed");
        esp_err_t result = nvs_set_blob(handle, kNvsKeys[index], &value, sizeof(value));
        if (result == ESP_OK) result = nvs_commit(handle);
        nvs_close(handle);
        if (result != ESP_OK) return result;
    }
    std::lock_guard<std::mutex> lock(mutex_);
    calibration_[index] = value;
    output_locked(pose_);
    return ESP_OK;
}

ServoCalibration OttoMotion::calibration(Servo servo) const {
    std::lock_guard<std::mutex> lock(mutex_);
    const size_t index = static_cast<size_t>(servo);
    return index < calibration_.size() ? calibration_[index] : ServoCalibration{};
}

void OttoMotion::output_locked(const Pose &pose) {
    if (!output_enabled_) return;
    for (size_t i = 0; i < pose.size(); ++i) {
        const auto &cal = calibration_[i];
        const float physical = std::clamp(cal.neutral + cal.direction * (clamp_angle(pose[i]) - 90.0f) +
                                              cal.trim, cal.minimum, cal.maximum);
        const float pulse_us = kMinPulseUs + physical * (kMaxPulseUs - kMinPulseUs) / 180.0f;
        const uint32_t duty = static_cast<uint32_t>(std::lround(pulse_us * kDutyResolution * kPwmHz / 1000000.0f));
        ledc_set_duty(LEDC_LOW_SPEED_MODE, kChannels[i], duty);
        ledc_update_duty(LEDC_LOW_SPEED_MODE, kChannels[i]);
    }
}

void OttoMotion::set_pose(const Pose &target) {
    std::lock_guard<std::mutex> lock(mutex_);
    for (size_t i = 0; i < pose_.size(); ++i) pose_[i] = clamp_angle(target[i]);
    move_duration_ms_ = 0;
    output_locked(pose_);
}

void OttoMotion::move_to(const Pose &target, uint32_t duration_ms, uint64_t now_ms) {
    std::lock_guard<std::mutex> lock(mutex_);
    move_start_ = pose_;
    for (size_t i = 0; i < move_target_.size(); ++i) move_target_[i] = clamp_angle(target[i]);
    move_start_ms_ = now_ms;
    move_duration_ms_ = duration_ms;
    if (duration_ms == 0) {
        pose_ = move_target_;
        output_locked(pose_);
    }
}

void OttoMotion::tick(uint64_t now_ms) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (move_duration_ms_ == 0) return;
    const uint64_t elapsed = now_ms >= move_start_ms_ ? now_ms - move_start_ms_ : 0;
    const float u = std::min(1.0f, float(elapsed) / float(move_duration_ms_));
    const float eased = u * u * (3.0f - 2.0f * u);
    for (size_t i = 0; i < pose_.size(); ++i) {
        pose_[i] = move_start_[i] + (move_target_[i] - move_start_[i]) * eased;
    }
    output_locked(pose_);
    if (u >= 1.0f) move_duration_ms_ = 0;
}

void OttoMotion::home(uint32_t duration_ms, uint64_t now_ms) {
    move_to({90, 90, 100, 90}, duration_ms, now_ms);
}

void OttoMotion::hold() {
    std::lock_guard<std::mutex> lock(mutex_);
    move_duration_ms_ = 0;
}

void OttoMotion::detach() {
    enable_output(false);
}

bool OttoMotion::moving() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return move_duration_ms_ > 0;
}

bool OttoMotion::enable_output(bool enabled) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!output_available_) return false;
    output_enabled_ = enabled;
    if (enabled) output_locked(pose_);
    else for (auto channel : kChannels) ledc_stop(LEDC_LOW_SPEED_MODE, channel, 0);
    return true;
}

Pose OttoMotion::pose() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return pose_;
}

} // namespace otto
