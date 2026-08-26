cmake_minimum_required(VERSION 3.16)

# This project has no registry-managed components; configure/build must stay offline.
set(ENV{IDF_COMPONENT_MANAGER} "0")
list(APPEND EXTRA_COMPONENT_DIRS
    "${CMAKE_CURRENT_LIST_DIR}/../../third_party/esp_serial_slave_link"
)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(leshy2_s3)
