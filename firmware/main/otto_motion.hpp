#pragma once

#include <array>
#include <cstdint>
#include <mutex>
#include "board_profile.hpp"
#include "esp_err.h"
#include "motion_types.hpp"

namespace otto {

enum class Servo : uint8_t { LeftLeg, RightLeg, LeftFoot, RightFoot };

struct ServoCalibration {
    float neutral = 90.0f;
    float trim = 0.0f;
    int8_t direction = 1;
    float minimum = 0.0f;
    float maximum = 180.0f;
};

class OttoMotion {
public:
    esp_err_t init(const BoardProfile &profile, bool allow_output);
    esp_err_t set_calibration(Servo servo, const ServoCalibration &calibration, bool persist);
    ServoCalibration calibration(Servo servo) const;
    void set_pose(const Pose &pose);
    void move_to(const Pose &pose, uint32_t duration_ms, uint64_t now_ms);
    void tick(uint64_t now_ms);
    void home(uint32_t duration_ms, uint64_t now_ms);
    void hold();
    void detach();
    Pose pose() const;
    bool output_enabled() const { return output_enabled_; }
    bool output_available() const { return output_available_; }
    bool moving() const;
    bool enable_output(bool enabled);

private:
    void output_locked(const Pose &pose);
    void load_calibration();
    static bool valid_calibration(const ServoCalibration &calibration);

    mutable std::mutex mutex_;
    std::array<ServoCalibration, 4> calibration_{};
    Pose pose_{90, 90, 100, 90};
    Pose move_start_{90, 90, 90, 90};
    Pose move_target_{90, 90, 90, 90};
    uint64_t move_start_ms_ = 0;
    uint32_t move_duration_ms_ = 0;
    bool output_enabled_ = false;
    bool output_available_ = false;
};

} // namespace otto
