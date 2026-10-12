#include "wifi_http.hpp"
#include "protocol.hpp"
#include "audio_output.hpp"
#include "audio_input.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cstdio>
#include <cstring>
#include <string>
#include "cJSON.h"
#include "esp_check.h"
#include "esp_http_server.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "esp_mac.h"
#include "esp_heap_caps.h"
#include "freertos/idf_additions.h"
#include "nvs_flash.h"
#include "robot.hpp"
#include "sdkconfig.h"

#ifndef CONFIG_OTTO_WIFI_SSID
#define CONFIG_OTTO_WIFI_SSID "YOUR_WIFI_SSID"
#endif
#ifndef CONFIG_OTTO_WIFI_PASSWORD
#define CONFIG_OTTO_WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#endif

namespace otto_wifi {
namespace {
constexpr char TAG[] = "otto_wifi";
otto::Robot *g_robot = nullptr;
httpd_handle_t g_server = nullptr;
httpd_handle_t g_audio_server = nullptr;
esp_netif_t *g_sta_netif = nullptr;
std::atomic<bool> g_audio_busy{false};
unsigned g_wifi_failures = 0;
bool g_wifi_fallback = false;

void set_wifi_network(bool fallback) {
    wifi_config_t sta = {};
    const char *ssid = fallback ? CONFIG_OTTO_WIFI_FALLBACK_SSID : CONFIG_OTTO_WIFI_SSID;
    const char *password = fallback ? CONFIG_OTTO_WIFI_FALLBACK_PASSWORD : CONFIG_OTTO_WIFI_PASSWORD;
    std::snprintf(reinterpret_cast<char *>(sta.sta.ssid), sizeof(sta.sta.ssid), "%s", ssid);
    std::snprintf(reinterpret_cast<char *>(sta.sta.password), sizeof(sta.sta.password), "%s", password);
    sta.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &sta));
    g_wifi_fallback = fallback;
}

struct AudioJob { uint8_t *pcm; size_t size; };

void play_audio_task(void *argument) {
    auto *job = static_cast<AudioJob *>(argument);
    const esp_err_t result = otto_audio::write_pcm16(reinterpret_cast<int16_t *>(job->pcm),job->size/2);
    if (result != ESP_OK) ESP_LOGE(TAG,"Speaker playback failed: %s",esp_err_to_name(result));
    heap_caps_free(job->pcm);
    delete job;
    g_audio_busy = false;
    vTaskDeleteWithCaps(nullptr);
}

void reply_json(httpd_req_t *req, const std::string &json, int status = 200) {
    httpd_resp_set_status(req, status == 200 ? "200 OK" : "400 Bad Request");
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    httpd_resp_send(req, json.c_str(), json.size());
}

std::string body(httpd_req_t *req) {
    if (req->content_len == 0 || req->content_len > 65536) return {};
    std::string value(req->content_len, '\0');
    size_t received = 0;
    while (received < value.size()) {
        const int count = httpd_req_recv(req, value.data() + received, value.size() - received);
        if (count <= 0) return {};
        received += size_t(count);
    }
    return value;
}

esp_err_t handler(httpd_req_t *req) {
    const std::string path(req->uri);
    if (path == "/api/audio/mic" && req->method == HTTP_GET) {
        if (!otto_mic::available()) { reply_json(req,R"({"error":"microphone unavailable"})",400); return ESP_OK; }
        httpd_resp_set_type(req, "application/octet-stream");
        httpd_resp_set_hdr(req, "Cache-Control", "no-store");
        static std::array<int16_t,512> samples;
        for (int i=0;i<64;++i) { // 2.048 seconds of 16 kHz mono PCM16.
            if (otto_mic::read_pcm16(samples.data(),samples.size()) != ESP_OK ||
                httpd_resp_send_chunk(req,reinterpret_cast<const char *>(samples.data()),samples.size()*sizeof(int16_t)) != ESP_OK)
                return ESP_FAIL;
        }
        return httpd_resp_send_chunk(req,nullptr,0);
    }
    if (path == "/api/audio/pcm" && req->method == HTTP_POST) {
        if (!otto_audio::available()) { reply_json(req,R"({"error":"speaker unavailable"})",400); return ESP_OK; }
        if (req->content_len == 0 || req->content_len % 2 || req->content_len > 4*1024*1024) {
            reply_json(req,R"({"error":"expected 24 kHz mono signed 16-bit PCM"})",400); return ESP_OK;
        }
        if (g_audio_busy.exchange(true)) { reply_json(req,R"({"error":"speaker busy"})",400); return ESP_OK; }
        uint8_t *pcm = static_cast<uint8_t *>(heap_caps_malloc(req->content_len,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT));
        if (!pcm) { g_audio_busy=false; reply_json(req,R"({"error":"audio buffer unavailable"})",400); return ESP_OK; }
        size_t remaining=req->content_len;
        size_t offset=0;
        while (remaining) {
            const int got=httpd_req_recv(req,reinterpret_cast<char *>(pcm+offset),std::min(remaining,size_t(4096)));
            if (got<=0) { heap_caps_free(pcm); g_audio_busy=false; httpd_resp_send_err(req,HTTPD_400_BAD_REQUEST,"audio transfer interrupted"); return ESP_FAIL; }
            remaining-=got;
            offset+=got;
        }
        auto *job = new AudioJob{pcm,offset};
        if (xTaskCreateWithCaps(play_audio_task,"otto_audio",8192,job,5,nullptr,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT)!=pdPASS) {
            heap_caps_free(pcm); delete job; g_audio_busy=false;
            reply_json(req,R"({"error":"audio task unavailable"})",400); return ESP_OK;
        }
        reply_json(req,R"({"accepted":true})"); return ESP_OK;
    }
    if (req->method == HTTP_OPTIONS) {
        httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
        httpd_resp_set_hdr(req, "Access-Control-Allow-Methods", "GET,POST,OPTIONS");
        httpd_resp_set_hdr(req, "Access-Control-Allow-Headers", "Content-Type");
        httpd_resp_send(req, nullptr, 0);
        return ESP_OK;
    }
    if (req->method == HTTP_POST || req->method == HTTP_GET) {
        auto result=otto_protocol::dispatch(path, req->method==HTTP_POST ? body(req) : "{}");
        reply_json(req,result.json,result.status); return ESP_OK;
    }
    httpd_resp_send_err(req, HTTPD_404_NOT_FOUND, "not found");
    return ESP_FAIL;
}

void on_wifi_event(void *, esp_event_base_t base, int32_t id, void *data) {
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        // Wi-Fi loss must not interrupt a program being controlled over BLE.
        if (CONFIG_OTTO_WIFI_FALLBACK_SSID[0] && ++g_wifi_failures >= 4) {
            g_wifi_failures = 0;
            set_wifi_network(!g_wifi_fallback);
        }
        ESP_LOGW(TAG, "Wi-Fi disconnected; retrying %s network",g_wifi_fallback ? "second" : "primary");
        esp_wifi_connect();
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        g_wifi_failures = 0;
        auto *event = static_cast<ip_event_got_ip_t *>(data);
        ESP_LOGI(TAG, "Wi-Fi connected, IP=" IPSTR, IP2STR(&event->ip_info.ip));
    }
}

void wifi_init() {
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    g_sta_netif = esp_netif_create_default_wifi_sta();
    wifi_init_config_t config = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&config));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &on_wifi_event, nullptr));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &on_wifi_event, nullptr));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    set_wifi_network(false);
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_ERROR_CHECK(esp_wifi_set_ps(WIFI_PS_NONE));
}
}

esp_err_t start(otto::Robot *robot) {
    if (!robot) return ESP_ERR_INVALID_ARG;
    g_robot = robot;
    wifi_init();
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.max_uri_handlers = 20;
    config.max_open_sockets = 5;
    config.stack_size = 8192;
    config.server_port = 80;
    ESP_RETURN_ON_ERROR(httpd_start(&g_server, &config), TAG, "http server start failed");
    static const char *paths[] = {"/api/status", "/api/play", "/api/servo", "/api/stop", "/api/home", "/api/face", "/api/output", "/api/audio/mic"};
    for (const char *path : paths) {
        httpd_uri_t uri = {};
        uri.uri = path;
        uri.method = (std::strcmp(path, "/api/status") == 0 || std::strcmp(path, "/api/audio/mic") == 0) ? HTTP_GET : HTTP_POST;
        uri.handler = handler;
        ESP_RETURN_ON_ERROR(httpd_register_uri_handler(g_server, &uri), TAG, "route registration failed");
        uri.method = HTTP_OPTIONS;
        ESP_RETURN_ON_ERROR(httpd_register_uri_handler(g_server, &uri), TAG, "OPTIONS registration failed");
    }
    httpd_config_t audio_config = HTTPD_DEFAULT_CONFIG();
    audio_config.server_port = 81;
    audio_config.ctrl_port = config.ctrl_port + 1;
    audio_config.stack_size = 6144;
    audio_config.max_open_sockets = 2;
    ESP_RETURN_ON_ERROR(httpd_start(&g_audio_server, &audio_config), TAG, "audio server start failed");
    httpd_uri_t audio_uri = {};
    audio_uri.uri = "/api/audio/pcm";
    audio_uri.method = HTTP_POST;
    audio_uri.handler = handler;
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(g_audio_server, &audio_uri), TAG, "audio route registration failed");
    ESP_LOGI(TAG, "Wi-Fi STA connecting to configured 2.4 GHz network; HTTP server port 80");
    return ESP_OK;
}

} // namespace otto_wifi
