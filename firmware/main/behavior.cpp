#include "behavior.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include "cJSON.h"
#include "esp_log.h"
#include "esp_timer.h"

namespace otto {
namespace {
constexpr auto kTag = "behavior";
constexpr uint32_t kTickMs = 10;
uint64_t now_ms() { return uint64_t(esp_timer_get_time()) / 1000; }
}

bool BehaviorEngine::safe_name(const std::string &name) {
    if (name.empty() || name.size() > 40) return false;
    return std::all_of(name.begin(), name.end(), [](unsigned char c) {
        return (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_';
    });
}

bool BehaviorEngine::parse_json(const std::string &json, Behavior &out, std::string &error) {
    cJSON *root = cJSON_ParseWithLength(json.data(), json.size());
    if (!root) { error = "invalid JSON"; return false; }
    Behavior value;
    const auto *repeat=cJSON_GetObjectItemCaseSensitive(root,"repeat");
    if (repeat && !cJSON_IsBool(repeat)) { error="repeat must be boolean"; cJSON_Delete(root); return false; }
    value.repeat=cJSON_IsTrue(repeat);
    const auto *reset_phase=cJSON_GetObjectItemCaseSensitive(root,"reset_phase_on_repeat");
    if (reset_phase && !cJSON_IsBool(reset_phase)) { error="reset_phase_on_repeat must be boolean"; cJSON_Delete(root); return false; }
    value.reset_phase_on_repeat=cJSON_IsTrue(reset_phase);
    const cJSON *name = cJSON_GetObjectItemCaseSensitive(root, "name");
    const cJSON *segments = cJSON_GetObjectItemCaseSensitive(root, "segments");
    if (cJSON_IsArray(segments)) {
        auto fail = [&]() { error="invalid motor program"; cJSON_Delete(root); return false; };
        if (!cJSON_IsString(name) || !safe_name(name->valuestring) || !segments->child) return fail();
        value.name=name->valuestring;
        uint64_t total=0;
        auto array = [](const cJSON *obj,const char *key,Pose &out,float low,float high) {
            const auto *a=cJSON_GetObjectItemCaseSensitive(obj,key);
            if (!cJSON_IsArray(a) || cJSON_GetArraySize(a)!=4) return false;
            for (int i=0;i<4;i++) {
                auto *n=cJSON_GetArrayItem(a,i);
                if (!cJSON_IsNumber(n) || !std::isfinite(n->valuedouble) || n->valuedouble<low || n->valuedouble>high) return false;
                out[i]=n->valuedouble;
            }
            return true;
        };
        for (auto *entry=segments->child;entry;entry=entry->next) {
            MotorSegment segment;
            auto *type=cJSON_GetObjectItemCaseSensitive(entry,"type");
            auto *duration=cJSON_GetObjectItemCaseSensitive(entry,"duration");
            if (!cJSON_IsString(type) || !cJSON_IsNumber(duration) || !std::isfinite(duration->valuedouble) ||
                duration->valuedouble<1 || duration->valuedouble>UINT32_MAX || std::floor(duration->valuedouble)!=duration->valuedouble) return fail();
            segment.duration_ms=duration->valuedouble; total+=segment.duration_ms;
            if (total>UINT32_MAX) return fail();
            std::string kind=type->valuestring;
            if (kind=="move") {
                segment.type=MotorSegment::Move;
                if (!array(entry,"pose",segment.target,0,180)) return fail();
            } else if (kind=="oscillate") {
                segment.type=MotorSegment::Oscillate;
                auto *period=cJSON_GetObjectItemCaseSensitive(entry,"period");
                if (!cJSON_IsNumber(period) || period->valuedouble<1 || period->valuedouble>UINT32_MAX || std::floor(period->valuedouble)!=period->valuedouble ||
                    !array(entry,"amplitude",segment.amplitude,-180,180) || !array(entry,"offset",segment.offset,-180,180) ||
                    !array(entry,"phase",segment.phase,-360000,360000)) return fail();
                segment.period_ms=period->valuedouble;
                for (int i=0;i<4;i++) if (90+segment.offset[i]-std::abs(segment.amplitude[i])<0 ||
                                          90+segment.offset[i]+std::abs(segment.amplitude[i])>180) return fail();
            } else if (kind=="output") {
                segment.type=MotorSegment::Output;
                auto *enabled=cJSON_GetObjectItemCaseSensitive(entry,"enabled");
                if (!cJSON_IsBool(enabled)) return fail();
                segment.enabled=cJSON_IsTrue(enabled);
            } else if (kind!="hold") return fail();
            value.segments.push_back(segment);
        }
        value.duration_ms=total; out=std::move(value); cJSON_Delete(root); return true;
    }
    const cJSON *duration = cJSON_GetObjectItemCaseSensitive(root, "duration");
    const cJSON *frames = cJSON_GetObjectItemCaseSensitive(root, "frames");
    if (!cJSON_IsString(name) || !name->valuestring || !safe_name(name->valuestring) ||
        !cJSON_IsNumber(duration) || !std::isfinite(duration->valuedouble) ||
        duration->valuedouble < 1 || duration->valuedouble > UINT32_MAX ||
        std::floor(duration->valuedouble) != duration->valuedouble ||
        !cJSON_IsArray(frames) || cJSON_GetArraySize(frames) < 2) {
        error = "invalid name, duration, or frame count";
        cJSON_Delete(root);
        return false;
    }
    value.name = name->valuestring;
    value.duration_ms = uint32_t(duration->valuedouble);
    uint32_t previous_time = 0;
    for (int i = 0; i < cJSON_GetArraySize(frames); ++i) {
        const cJSON *frame_json = cJSON_GetArrayItem(frames, i);
        const cJSON *time = cJSON_GetObjectItemCaseSensitive(frame_json, "time");
        const cJSON *servo = cJSON_GetObjectItemCaseSensitive(frame_json, "servo");
        const cJSON *expression = cJSON_GetObjectItemCaseSensitive(frame_json, "expression");
        if (!cJSON_IsObject(frame_json) || !cJSON_IsNumber(time) ||
            !std::isfinite(time->valuedouble) || time->valuedouble < 0 ||
            time->valuedouble > value.duration_ms ||
            std::floor(time->valuedouble) != time->valuedouble ||
            (i == 0 && time->valuedouble != 0) ||
            (i > 0 && time->valuedouble <= previous_time) ||
            !cJSON_IsArray(servo) || cJSON_GetArraySize(servo) != 4 ||
            !cJSON_IsString(expression) || !expression->valuestring ||
            !safe_name(expression->valuestring)) {
            error = "invalid frame time, servo array, or expression ID";
            cJSON_Delete(root);
            return false;
        }
        RobotFrame frame;
        frame.time_ms = uint32_t(time->valuedouble);
        frame.expression = expression->valuestring;
        previous_time = frame.time_ms;
        for (int axis = 0; axis < 4; ++axis) {
            const cJSON *angle = cJSON_GetArrayItem(servo, axis);
            if (!cJSON_IsNumber(angle) || !std::isfinite(angle->valuedouble) ||
                angle->valuedouble < 0 || angle->valuedouble > 180) {
                error = "servo angle must be finite and within 0..180";
                cJSON_Delete(root);
                return false;
            }
            frame.servo[axis] = float(angle->valuedouble);
        }
        value.frames.emplace_back(std::move(frame));
    }
    cJSON_Delete(root);
    if (value.frames.back().time_ms != value.duration_ms) {
        error = "last frame must match duration";
        return false;
    }
    out = std::move(value);
    return true;
}

esp_err_t BehaviorEngine::init(OttoMotion *motion, RobotFace *face) {
    if (!motion || !face) return ESP_ERR_INVALID_ARG;
    motion_ = motion;
    face_ = face;
    return xTaskCreatePinnedToCore(task_entry, "otto_behavior", 8192, this, 5, &task_, 1) == pdPASS
               ? ESP_OK : ESP_ERR_NO_MEM;
}

bool BehaviorEngine::play(const std::string &name, Priority priority) {
    if (!safe_name(name)) return false;
    const std::string path = "/spiffs/behavior/" + name + ".json";
    FILE *file = std::fopen(path.c_str(), "rb");
    if (!file) { ESP_LOGE(kTag, "missing behavior: %s", path.c_str()); return false; }
    std::fseek(file, 0, SEEK_END);
    const long length = std::ftell(file);
    std::rewind(file);
    if (length <= 0 || length > 16384) { std::fclose(file); return false; }
    std::string json(static_cast<size_t>(length), '\0');
    const size_t read = std::fread(json.data(), 1, json.size(), file);
    std::fclose(file);
    if (read != json.size()) return false;
    Behavior next;
    std::string error;
    if (!parse_json(json, next, error) || next.name != name) {
        ESP_LOGE(kTag, "invalid %s: %s", path.c_str(), error.c_str());
        return false;
    }
    for (const auto &frame : next.frames) {
        if (!face_->has_asset(frame.expression)) {
            ESP_LOGE(kTag, "unknown expression asset: %s", frame.expression.c_str());
            return false;
        }
    }
    return play_json(json, priority);
}

bool BehaviorEngine::play_json(const std::string &json, Priority priority) {
    Behavior next;
    std::string error;
    if (!parse_json(json, next, error)) {
        ESP_LOGE(kTag, "invalid behavior JSON: %s", error.c_str());
        return false;
    }
    for (const auto &frame : next.frames) {
        if (!face_->has_asset(frame.expression)) {
            ESP_LOGE(kTag, "unknown expression asset: %s", frame.expression.c_str());
            return false;
        }
    }
    const uint64_t now = now_ms();
    std::lock_guard<std::mutex> lock(mutex_);
    if (!motion_->output_enabled()) return false;
    blend_from_ = motion_->pose();
    blend_started_ms_ = now;
    active_ = std::move(next);
    priority_ = priority;
    started_ms_ = now;
    segment_started_ms_ = now;
    segment_index_ = 0;
    oscillator_cycles_ = 0;
    segment_from_ = motion_->pose();
    last_expression_.clear();
    playing_ = true;
    return true;
}

void BehaviorEngine::stop() {
    std::lock_guard<std::mutex> lock(mutex_);
    playing_ = false;
    priority_ = Priority::Idle;
    active_ = {};
    last_expression_.clear();
    motion_->hold();
}

void BehaviorEngine::cancel() {
    std::lock_guard<std::mutex> lock(mutex_);
    playing_ = false;
    priority_ = Priority::Idle;
    active_ = {};
    last_expression_.clear();
    face_->reset();
    motion_->hold();
}

void BehaviorEngine::home() {
    std::lock_guard<std::mutex> lock(mutex_);
    playing_ = false;
    priority_ = Priority::Idle;
    active_ = {};
    face_->reset();
    last_expression_ = "smile_static";
    motion_->home(500, now_ms());
}

bool BehaviorEngine::set_face(const std::string &id, int loop_count) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!face_->has_asset(id)) return false;
    if (!face_->set_asset(id, loop_count)) return false;
    last_expression_ = id;
    return true;
}

std::string BehaviorEngine::expression() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return face_->current_asset();
}

bool BehaviorEngine::move_pose(const Pose &pose, uint32_t duration_ms) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (!motion_->output_enabled()) return false;
    playing_ = false;
    priority_ = Priority::Idle;
    active_ = {};
    motion_->move_to(pose, duration_ms, now_ms());
    return true;
}

bool BehaviorEngine::enable_output(bool enabled) {
    std::lock_guard<std::mutex> lock(mutex_);
    playing_ = false;
    priority_ = Priority::Idle;
    active_ = {};
    motion_->hold();
    return motion_->enable_output(enabled);
}

std::string BehaviorEngine::active_name() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return playing_ ? active_.name : std::string("idle");
}

bool BehaviorEngine::repeating() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return playing_ && active_.repeat;
}

void BehaviorEngine::task_entry(void *context) { static_cast<BehaviorEngine *>(context)->task_loop(); }

void BehaviorEngine::task_loop() {
    TickType_t wake = xTaskGetTickCount();
    while (true) {
        tick(now_ms());
        vTaskDelayUntil(&wake, pdMS_TO_TICKS(kTickMs));
    }
}

void BehaviorEngine::tick(uint64_t now) {
    {
        std::lock_guard<std::mutex> lock(mutex_);
        if (playing_ && !active_.segments.empty()) {
            // Advance each completed segment, preserving its exact endpoint even after a delayed tick.
            while (playing_) {
                const auto &segment=active_.segments[segment_index_];
                const uint64_t elapsed=now-segment_started_ms_;
                const uint32_t t=std::min<uint64_t>(elapsed,segment.duration_ms);
                Pose output=segment_from_;
                if (segment.type==MotorSegment::Move) {
                    const float u=float(t)/segment.duration_ms;
                    const float smooth=u*u*(3.0f-2.0f*u);
                    for (int i=0;i<4;i++) output[i]+=smooth*(segment.target[i]-output[i]);
                } else if (segment.type==MotorSegment::Oscillate) {
                    for (int i=0;i<4;i++) output[i]=90+segment.offset[i]+segment.amplitude[i]*
                        std::sin(6.283185307179586*(oscillator_cycles_+double(t)/segment.period_ms)+segment.phase[i]*0.017453292519943295);
                }
                if (segment.type==MotorSegment::Output) motion_->enable_output(segment.enabled);
                else if (segment.type!=MotorSegment::Hold) { if (!motion_->output_enabled()) motion_->enable_output(true); motion_->set_pose(output); }
                if (elapsed<segment.duration_ms) break;
                segment_from_=output; segment_started_ms_+=segment.duration_ms;
                if (segment.type==MotorSegment::Oscillate) oscillator_cycles_=std::fmod(oscillator_cycles_+double(segment.duration_ms)/segment.period_ms,1.0);
                if (segment.type==MotorSegment::Output && !segment.enabled) oscillator_cycles_=0;
                if (++segment_index_==active_.segments.size()) {
                    if (active_.repeat) { segment_index_=0; if (active_.reset_phase_on_repeat) oscillator_cycles_=0; }
                    else { playing_=false; priority_=Priority::Idle; }
                }
            }
        } else if (playing_) {
            const uint64_t elapsed = now >= started_ms_ ? now - started_ms_ : 0;
            const auto sample = sample_behavior(active_, uint32_t(std::min<uint64_t>(elapsed, UINT32_MAX)));
            Pose output = sample.servo;
            const uint64_t blend_elapsed = now >= blend_started_ms_ ? now - blend_started_ms_ : 0;
            if (blend_elapsed < 120) {
                const float u = float(blend_elapsed) / 120.0f;
                for (size_t i = 0; i < output.size(); ++i)
                    output[i] = blend_from_[i] + (output[i] - blend_from_[i]) * u;
            }
            motion_->set_pose(output);
            if (sample.expression != last_expression_) {
                if (!face_->set_asset(sample.expression))
                    ESP_LOGW(kTag, "missing face asset: %s", sample.expression.c_str());
                last_expression_ = sample.expression;
            }
            if (sample.finished) {
                playing_ = false;
                priority_ = Priority::Idle;
                // Hold the final frame; returning home is a separate explicit command.
            }
        } else {
            motion_->tick(now);
        }
        face_->tick(now);
    }
}

} // namespace otto
