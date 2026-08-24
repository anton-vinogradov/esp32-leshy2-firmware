cmake_minimum_required(VERSION 3.15)

set(PICO_SDK_FETCH_FROM_GIT OFF CACHE BOOL "Network SDK fetch is forbidden" FORCE)
set(PICO_BOARD_HEADER_DIRS "${CMAKE_CURRENT_LIST_DIR}/boards")
include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(leshy2_rp C CXX ASM)
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

pico_sdk_init()

set(LESHY2_COMMON_DIR "${CMAKE_CURRENT_LIST_DIR}/../../common")
set(LESHY2_RP_PARTITION_SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../config/rp2354b_partitions.json")
if(NOT EXISTS "${LESHY2_RP_PARTITION_SOURCE}")
    message(FATAL_ERROR "Missing reviewed RP2354B partition source")
endif()
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${LESHY2_RP_PARTITION_SOURCE}")

add_executable(leshy2_rp
    main.c
    "${LESHY2_COMMON_DIR}/src/l2ip.c"
    "${LESHY2_COMMON_DIR}/src/safety_core.c"
    "${LESHY2_COMMON_DIR}/src/system_model.c"
    "${LESHY2_COMMON_DIR}/src/update_core.c"
)
target_include_directories(leshy2_rp PRIVATE "${LESHY2_COMMON_DIR}/include")
target_link_libraries(leshy2_rp PRIVATE pico_stdlib)

target_compile_options(leshy2_rp PRIVATE
    -std=c17
    -Wall
    -Wextra
    -Werror
    -Wformat=2
    -Wshadow
    -Wundef
    -Wconversion
    -Wdouble-promotion
    -Wmissing-prototypes
    -Wpedantic
    -Wstrict-prototypes
    -ffunction-sections
    -fdata-sections
    -fstack-usage
    "-ffile-prefix-map=${CMAKE_SOURCE_DIR}=."
    "-fdebug-prefix-map=${CMAKE_SOURCE_DIR}=."
    "$<$<CONFIG:Debug>:-Og>"
    "$<$<CONFIG:Debug>:-g3>"
    "$<$<CONFIG:Release>:-Os>"
    "$<$<CONFIG:Release>:-g1>"
)
target_compile_definitions(leshy2_rp PRIVATE "$<$<CONFIG:Release>:NDEBUG=1>")
target_link_options(leshy2_rp PRIVATE
    "-Wl,-Map=${CMAKE_BINARY_DIR}/leshy2_rp.map"
    "-Wl,--cref"
    "-Wl,--fatal-warnings"
    "-Wl,--gc-sections"
)

pico_add_extra_outputs(leshy2_rp)
