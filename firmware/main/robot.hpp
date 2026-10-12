#pragma once

#include <string>
#include "behavior.hpp"

namespace otto {

class Robot {
public:
    esp_err_t init();
    bool play_json(const std::string &json, Priority priority = Priority::Normal);
    bool move_pose(const Pose &pose, uint32_t duration_ms);
    void home();
    void stop();
    void emergency_detach();
    RobotFace &face() { return face_; }
    OttoMotion &motion() { return motion_; }
    BehaviorEngine &behavior() { return behavior_; }

private:
    BoardDisplay display_;
    RobotFace face_;
    OttoMotion motion_;
    BehaviorEngine behavior_;
};

} // namespace otto
