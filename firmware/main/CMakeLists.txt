idf_component_register(
    SRCS
        "main.cpp"
        "board_display.cpp"
        "otto_motion.cpp"
        "robot_face.cpp"
        "behavior.cpp"
        "robot.cpp"
        "wifi_http.cpp"
        "protocol.cpp"
        "ble_control.cpp"
        "audio_output.cpp"
        "audio_input.cpp"
    INCLUDE_DIRS "."
    REQUIRES bt esp_lcd esp_driver_spi esp_driver_ledc esp_driver_gpio esp_driver_i2s esp_timer nvs_flash spiffs esp_wifi esp_netif esp_http_server espressif__cjson espressif2022__esp_emote_gen_player
)
target_compile_features(${COMPONENT_LIB} PUBLIC cxx_std_17)
spiffs_create_partition_image(storage ../assets FLASH_IN_PROJECT)
