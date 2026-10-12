#pragma once

#include <algorithm>
#include <cstdint>
#include <cmath>
#include <string>
#include <vector>
#include "motion_types.hpp"

namespace otto {

struct RobotFrame {
    uint32_t time_ms = 0;
    Pose servo{90, 90, 90, 90};
    std::string expression;
};

struct MotorSegment {
    enum Type { Move, Hold, Oscillate, Output } type = Hold;
    uint32_t duration_ms = 0, period_ms = 1000;
    Pose target{}, amplitude{}, offset{}, phase{};
    bool enabled = true;
};

struct Behavior {
    bool repeat = false;
    bool reset_phase_on_repeat = false;
    std::string name;
    uint32_t duration_ms = 0;
    std::vector<RobotFrame> frames;
    std::vector<MotorSegment> segments;
};

struct BehaviorSample {
    Pose servo{90, 90, 90, 90};
    std::string expression;
    bool finished = false;
};

inline BehaviorSample sample_behavior(const Behavior &behavior, uint32_t elapsed_ms) {
    BehaviorSample sample;
    if (behavior.frames.empty()) return sample;
    const uint32_t time = std::min(elapsed_ms, behavior.duration_ms);
    sample.finished = elapsed_ms >= behavior.duration_ms;
    const auto upper = std::upper_bound(behavior.frames.begin(), behavior.frames.end(), time,
                                      [](uint32_t value, const RobotFrame &frame) { return value < frame.time_ms; });
    const RobotFrame &left = upper == behavior.frames.begin() ? behavior.frames.front() : *(upper - 1);
    sample.expression = left.expression;
    sample.servo = left.servo;
    if (upper != behavior.frames.end() && upper->time_ms > left.time_ms) {
        const float u = float(time - left.time_ms) / float(upper->time_ms - left.time_ms);
        const float smooth = u * u * (3.0f - 2.0f * u);
        for (size_t i = 0; i < sample.servo.size(); ++i) {
            sample.servo[i] += (upper->servo[i] - left.servo[i]) * smooth;
        }
    }
    return sample;
}

} // namespace otto
