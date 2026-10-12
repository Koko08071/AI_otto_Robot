cmake_minimum_required(VERSION 3.16)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(otto_expression_motion)

esptool_py_flash_to_partition(flash "emote_gen" "${CMAKE_CURRENT_SOURCE_DIR}/../expressions/official/all_emote_assets.bin")
