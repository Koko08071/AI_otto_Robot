#include "protocol.hpp"
#include "cJSON.h"
#include "esp_mac.h"
#include "esp_timer.h"
#include "esp_system.h"
#include "esp_heap_caps.h"
#include "audio_output.hpp"
#include "audio_input.hpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
namespace otto_protocol {
static otto::Robot *g_robot;
void init(otto::Robot *robot) { g_robot=robot; }
int number(const cJSON *object, const char *name, int fallback) {
    const auto *value = cJSON_GetObjectItemCaseSensitive(object, name);
    return cJSON_IsNumber(value) ? value->valueint : fallback;
}

Reply command(const std::string &path, const std::string &payload) {
    if (path == "/api/stop" || path == "/api/home") {
        otto_audio::stop();
        if (path == "/api/home") g_robot->home();
        else g_robot->stop();
        return {R"({"accepted":true,"action":"stop"})", 200};
    }
    cJSON *root = cJSON_ParseWithLength(payload.data(), payload.size());
    if (!root) { return {R"({"error":"invalid JSON"})", 400}; }
    const int priority = std::clamp(number(root, "priority", int(otto::Priority::Normal)), 0, 4);
    bool accepted = false;
    if (path == "/api/face") {
        const auto *expression = cJSON_GetObjectItemCaseSensitive(root, "expression");
        const auto *loops = cJSON_GetObjectItemCaseSensitive(root, "loopCount");
        int loop_count = cJSON_IsNumber(loops) ? int(loops->valuedouble) : 0;
        if (loop_count < 0) loop_count = 0;
        if (loop_count > 99) loop_count = 99;
        accepted = cJSON_IsString(expression) &&
                   g_robot->behavior().set_face(expression->valuestring, loop_count);
    } else if (path == "/api/output") {
        const auto *enabled = cJSON_GetObjectItemCaseSensitive(root, "enabled");
        accepted = cJSON_IsBool(enabled) &&
                   g_robot->behavior().enable_output(cJSON_IsTrue(enabled));
    } else if (path == "/api/servo") {
        const auto *pose_json = cJSON_GetObjectItemCaseSensitive(root, "pose");
        const int duration = number(root, "duration", 300);
        if (duration < 1) { cJSON_Delete(root); return {R"({"error":"duration must be positive"})",400}; }
        otto::Pose pose{90, 90, 90, 90};
        if (cJSON_IsArray(pose_json) && cJSON_GetArraySize(pose_json) == 4) {
            for (int i = 0; i < 4; ++i) {
                const auto *angle = cJSON_GetArrayItem(pose_json, i);
                if (!cJSON_IsNumber(angle) || angle->valuedouble < 0 || angle->valuedouble > 180) {
                    cJSON_Delete(root);
                    return {R"({"error":"angle must be between 0 and 180"})", 400};
                }
                pose[i] = float(angle->valuedouble);
            }
            accepted = g_robot->move_pose(pose, duration);
        }
    } else if (path == "/api/play") {
        char *printed = cJSON_PrintUnformatted(root);
        accepted = printed && g_robot->play_json(printed, static_cast<otto::Priority>(priority));
        if (printed) cJSON_free(printed);
    }
    cJSON_Delete(root);
    return {accepted ? R"({"accepted":true})" : R"({"accepted":false,"error":"command rejected"})", accepted ? 200 : 400};
}


Reply status() {
        const auto pose = g_robot->motion().pose();
        cJSON *root = cJSON_CreateObject();
        cJSON_AddBoolToObject(root, "connected", true);
        cJSON_AddNumberToObject(root,"display_flush_us",g_robot->face().display_flush_us());
        cJSON_AddNumberToObject(root,"displayed_frames",g_robot->face().displayed_frames());
        cJSON_AddNumberToObject(root,"uptime_ms",esp_timer_get_time()/1000);
        cJSON_AddNumberToObject(root,"heap",heap_caps_get_free_size(MALLOC_CAP_INTERNAL));
        cJSON_AddNumberToObject(root,"reset_reason",esp_reset_reason());
        cJSON_AddBoolToObject(root,"repeat",g_robot->behavior().repeating());
        cJSON_AddStringToObject(root, "active", g_robot->behavior().active_name().c_str());
        uint8_t mac[6];
        esp_read_mac(mac, ESP_MAC_WIFI_STA);
        char id[18];
        std::snprintf(id, sizeof(id), "%02x:%02x:%02x:%02x:%02x:%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
        cJSON_AddStringToObject(root, "device_id", id);
        cJSON_AddStringToObject(root, "board", otto::board_profile().name);
        cJSON_AddStringToObject(root, "screen", otto::board_profile().valid ? "st7789" : "disabled");
        cJSON_AddBoolToObject(root, "servo_enabled", g_robot->motion().output_enabled());
        cJSON_AddBoolToObject(root, "servo_available", g_robot->motion().output_available());
        cJSON_AddBoolToObject(root, "audio_available", otto_audio::available());
        cJSON_AddBoolToObject(root, "mic_available", otto_mic::available());
        cJSON_AddBoolToObject(root, "moving", g_robot->motion().moving());
        cJSON_AddStringToObject(root, "expression", g_robot->behavior().expression().c_str());
        cJSON *array = cJSON_AddArrayToObject(root, "pose");
        for (float value : pose) cJSON_AddItemToArray(array, cJSON_CreateNumber(value));
        char *json = cJSON_PrintUnformatted(root);
        Reply reply{json ? json : "{}",200};
        if (json) cJSON_free(json);
        cJSON_Delete(root);
        return reply;

}
Reply dispatch(const std::string &path,const std::string &payload) {
 if (path=="/api/status") return status();
 return command(path,payload);
}
}
