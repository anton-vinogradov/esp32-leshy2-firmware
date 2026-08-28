cmake_minimum_required(VERSION 3.15)

if(NOT DEFINED PICO_SDK_PATH OR PICO_SDK_PATH STREQUAL "")
    message(FATAL_ERROR "PICO_SDK_PATH must name the locked Pico SDK checkout")
endif()

get_filename_component(LESHY2_REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(PICO_SDK_FETCH_FROM_GIT OFF CACHE BOOL "Network SDK fetch is forbidden" FORCE)
set(FETCHCONTENT_FULLY_DISCONNECTED ON CACHE BOOL "Network fetches are forbidden" FORCE)
set(PICO_BOARD_HEADER_DIRS "${CMAKE_CURRENT_LIST_DIR}/boards")
include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(leshy2_rf_rp C CXX ASM)
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

pico_sdk_init()

set(LESHY2_GENERATED_R2_HW_DIR "${LESHY2_REPO_ROOT}/generated/r2/hardware")
add_executable(
    leshy2_rf_rp
    main.c
    "${LESHY2_GENERATED_R2_HW_DIR}/src/rf_rp_bsp.c"
)
target_include_directories(
    leshy2_rf_rp PRIVATE "${LESHY2_GENERATED_R2_HW_DIR}/include"
)
target_compile_definitions(leshy2_rf_rp PRIVATE LESHY2_TARGET_RF_RP=1)
target_compile_options(leshy2_rf_rp PRIVATE
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
    "-ffile-prefix-map=${LESHY2_REPO_ROOT}=."
    "-fdebug-prefix-map=${LESHY2_REPO_ROOT}=."
    "$<$<CONFIG:Debug>:-Og>"
    "$<$<CONFIG:Debug>:-g3>"
    "$<$<CONFIG:Release>:-Os>"
    "$<$<CONFIG:Release>:-g1>"
)
target_compile_definitions(leshy2_rf_rp PRIVATE "$<$<CONFIG:Release>:NDEBUG=1>")
target_link_options(leshy2_rf_rp PRIVATE
    "-Wl,--cref"
    "-Wl,--fatal-warnings"
    "-Wl,--gc-sections"
)
target_link_libraries(leshy2_rf_rp PRIVATE pico_stdlib)

pico_add_extra_outputs(leshy2_rf_rp)
