#pragma once
#include <string>
#include "robot.hpp"
namespace otto_protocol {
struct Reply { std::string json; int status; };
void init(otto::Robot *robot);
Reply dispatch(const std::string &path,const std::string &payload);
}
