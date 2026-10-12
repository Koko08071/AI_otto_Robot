#pragma once
#include <string>
#include <atomic>
#include "board_display.hpp"
#include "emote_gen_player.h"
namespace otto {
enum class Face { Idle, Happy, Sad, Angry, Surprised, Confused, Sleepy, Listening, Thinking, Speaking, Error };
class RobotFace {
public:
    esp_err_t init(BoardDisplay *display);
    esp_err_t load_assets(const char *unused);
    bool set(Face face);
    bool set_asset(const std::string &id, int loop_count = 0);
    bool has_asset(const std::string &id) const;
    void reset() { set_asset("smile_static"); }
    void tick(uint64_t) {}
    const std::string &current_asset() const { return asset_id_; }
    uint32_t display_flush_us() const { return display_flush_us_.load(); }
    uint32_t displayed_frames() const { return displayed_frames_.load(); }
private:
    std::atomic<uint32_t> displayed_frames_{0};
    std::atomic<uint32_t> display_flush_us_{0};
    BoardDisplay *display_ = nullptr;
    emote_gen_player_handle_t player_ = nullptr;
    std::string asset_id_ = "smile_static";
    static RobotFace *active_player_;
    static void flush_callback(int,int,int,int,const void *,emote_gen_player_handle_t);
};
}
