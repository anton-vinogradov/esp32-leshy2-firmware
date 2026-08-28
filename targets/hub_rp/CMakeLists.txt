cmake_minimum_required(VERSION 3.15)

if(NOT DEFINED PICO_SDK_PATH OR PICO_SDK_PATH STREQUAL "")
    message(FATAL_ERROR "PICO_SDK_PATH must name the locked Pico SDK checkout")
endif()

get_filename_component(LESHY2_REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(PICO_SDK_FETCH_FROM_GIT OFF CACHE BOOL "Network SDK fetch is forbidden" FORCE)
set(FETCHCONTENT_FULLY_DISCONNECTED ON CACHE BOOL "Network fetches are forbidden" FORCE)
set(PICO_BOARD_HEADER_DIRS "${CMAKE_CURRENT_LIST_DIR}/boards")
include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

project(leshy2_hub_rp C CXX ASM)
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
# Pico SDK interface sources use GNU C constructs such as `asm`.  The Leshy2
# sources below still receive an explicit -std=c17 through source properties.
set(CMAKE_C_EXTENSIONS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

pico_sdk_init()

set(LESHY2_GENERATED_R2_HW_DIR "${LESHY2_REPO_ROOT}/generated/r2/hardware")
set(LESHY2_HUB_RP_PROJECT_SOURCES
    main.c
    "${LESHY2_GENERATED_R2_HW_DIR}/src/hub_rp_bsp.c"
)
add_executable(leshy2_hub_rp ${LESHY2_HUB_RP_PROJECT_SOURCES})
target_include_directories(
    leshy2_hub_rp PRIVATE "${LESHY2_GENERATED_R2_HW_DIR}/include"
)
target_compile_definitions(leshy2_hub_rp PRIVATE LESHY2_TARGET_HUB_RP=1)
set(LESHY2_HUB_RP_PROJECT_COMPILE_OPTIONS
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
set_source_files_properties(
    ${LESHY2_HUB_RP_PROJECT_SOURCES}
    PROPERTIES COMPILE_OPTIONS "${LESHY2_HUB_RP_PROJECT_COMPILE_OPTIONS}"
)
target_compile_definitions(leshy2_hub_rp PRIVATE "$<$<CONFIG:Release>:NDEBUG=1>")
target_link_options(leshy2_hub_rp PRIVATE
    "-Wl,--cref"
    "-Wl,--fatal-warnings"
    "-Wl,--gc-sections"
)
target_link_libraries(leshy2_hub_rp PRIVATE pico_stdlib)

pico_add_extra_outputs(leshy2_hub_rp)
