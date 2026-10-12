#include "robot.hpp"
#include "wifi_http.hpp"
#include "ble_control.hpp"
#include "protocol.hpp"
#include "audio_output.hpp"
#include "audio_input.hpp"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "cJSON.h"

static otto::Robot robot;

extern "C" void app_main() {
    // Large editable programs contain many small JSON nodes. Keep these in PSRAM
    // so BLE and LCD DMA retain their required internal memory.
    cJSON_Hooks hooks={};
    hooks.malloc_fn=[](size_t size)->void * { return heap_caps_malloc(size,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT); };
    hooks.free_fn=heap_caps_free;
    cJSON_InitHooks(&hooks);
    const esp_err_t result = robot.init();
    if (result != ESP_OK) {
        ESP_LOGE("main", "Robot initialization failed: %s", esp_err_to_name(result));
        return;
    }
    otto_protocol::init(&robot);
    const esp_err_t audio_result = otto_audio::init();
    if (audio_result != ESP_OK) ESP_LOGE("main", "Speaker initialization failed: %s", esp_err_to_name(audio_result));
    const esp_err_t mic_result = otto_mic::init();
    if (mic_result != ESP_OK) ESP_LOGE("main", "Microphone initialization failed: %s", esp_err_to_name(mic_result));
    ESP_ERROR_CHECK(otto_ble::start());
    const esp_err_t wifi_result = otto_wifi::start(&robot);
    if (wifi_result != ESP_OK) {
        ESP_LOGE("main", "Wi-Fi control server failed: %s", esp_err_to_name(wifi_result));
        return;
    }
    // Wi-Fi and BLE share the same command dispatcher.
}
