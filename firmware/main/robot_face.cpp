#include "robot_face.hpp"
#include "esp_log.h"
#include "esp_timer.h"
namespace otto {
RobotFace *RobotFace::active_player_ = nullptr;
void RobotFace::flush_callback(int x0,int y0,int x1,int y1,const void *data,emote_gen_player_handle_t player) {
    if (active_player_ && active_player_->display_->submit_region(x0,y0,x1,y1,data)!=ESP_OK)
        ESP_LOGE("face","display flush failed");
    if (active_player_ && gfx_disp_is_flushing_last(emote_gen_player_get_disp(player))) {
        const auto start=esp_timer_get_time();
        if (active_player_->display_->flush_frame()==ESP_OK) ++active_player_->displayed_frames_;
        active_player_->display_flush_us_=esp_timer_get_time()-start;
    }
    emote_gen_player_notify_flush_finished(player);
}
esp_err_t RobotFace::init(BoardDisplay *display) {
    display_=display;
    if (!display || !display->available()) return ESP_ERR_INVALID_STATE;
    active_player_=this;
    emote_gen_player_config_t config={};
    config.flags.swap=true; config.flags.double_buffer=true; config.flags.buff_dma=true;
    config.gfx_emote.h_res=BoardDisplay::kAnimationSize;
    config.gfx_emote.v_res=BoardDisplay::kAnimationSize; config.gfx_emote.fps=25;
    config.buffers.buf_pixels=BoardDisplay::kAnimationSize*16;
    config.task.task_priority=5; config.task.task_stack=6144; config.task.task_affinity=0;
    config.flush_cb=flush_callback;
    player_=emote_gen_player_init(&config);
    return player_ ? ESP_OK : ESP_FAIL;
}
esp_err_t RobotFace::load_assets(const char *) {
    emote_gen_player_data_t source={}; source.type=EMOTE_GEN_PLAYER_SOURCE_PARTITION;
    source.source.partition_label="emote_gen"; source.flags.mmap_enable=1;
    auto result=emote_gen_player_mount_assets(player_,&source);
    if (result!=ESP_OK) return result;
    return set_asset("smile_static") ? ESP_OK : ESP_FAIL;
}
bool RobotFace::has_asset(const std::string &id) const {
    for (size_t i=0;i<emote_gen_player_get_index_count(player_);++i) {
        const auto *entry=emote_gen_player_get_index_entry(player_,i);
        if (entry && id==entry->name) return true;
    }
    return false;
}
bool RobotFace::set_asset(const std::string &id, int loop_count) {
    if (!has_asset(id)) return false;
    auto gfx=emote_gen_player_get_gfx_handle(player_);
    if (gfx_emote_lock(gfx)!=ESP_OK) return false;
    const auto clear_result=display_->clear();
    // loop_count<=1: play once through outro; 0 or >1: keep looping middle until replaced
    const bool repeat = loop_count == 0 || loop_count > 1;
    const auto result=clear_result==ESP_OK ? emote_gen_player_anim_now_name(player_,id.c_str(),repeat) : clear_result;
    if (result==ESP_OK) { emote_gen_player_set_tip_text(player_,""); asset_id_=id; }
    gfx_emote_unlock(gfx);
    return result==ESP_OK;
}
bool RobotFace::set(Face face) {
    static const char *names[]={"smile_static","smile_05s","sad_05s15s","angry_20s","shocked_05s_","question_05s","asleep_215s","investigate_","ponder_05s","laugh_05s_10","panic_05s_15"};
    auto i=static_cast<size_t>(face); return i<11 && set_asset(names[i]);
}
}
