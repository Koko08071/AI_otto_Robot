#pragma once

#include <cstdint>
#include <mutex>
#include <string>
#include "behavior_model.hpp"
#include "otto_motion.hpp"
#include "robot_face.hpp"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace otto {

enum class Priority : uint8_t { Idle = 0, Normal = 1, Interactive = 2, Event = 3, System = 4 };

class BehaviorEngine {
public:
    esp_err_t init(OttoMotion *motion, RobotFace *face);
    bool play(const std::string &name, Priority priority = Priority::Normal);
    bool play_json(const std::string &json, Priority priority = Priority::Normal);
    void stop();
    void cancel();
    void home();
    bool set_face(const std::string &id, int loop_count = 0);
    bool move_pose(const Pose &pose, uint32_t duration_ms);
    bool enable_output(bool enabled);
    std::string expression() const;
    std::string active_name() const;
    bool repeating() const;
    static bool parse_json(const std::string &json, Behavior &out, std::string &error);

private:
    static void task_entry(void *context);
    void task_loop();
    void tick(uint64_t now_ms);
    static bool safe_name(const std::string &name);

    OttoMotion *motion_ = nullptr;
    RobotFace *face_ = nullptr;
    TaskHandle_t task_ = nullptr;
    mutable std::mutex mutex_;
    Behavior active_;
    Priority priority_ = Priority::Idle;
    uint64_t started_ms_ = 0;
    uint64_t blend_started_ms_ = 0;
    Pose blend_from_{90, 90, 90, 90};
    std::string last_expression_;
    bool playing_ = false;
    size_t segment_index_ = 0;
    uint64_t segment_started_ms_ = 0;
    Pose segment_from_{};
    double oscillator_cycles_ = 0;
};

} // namespace otto
