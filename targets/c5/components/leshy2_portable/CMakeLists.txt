set(LESHY2_COMMON_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../../common")
set(LESHY2_GENERATED_HW_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../../generated/hardware")

idf_component_register(
    SRCS
        "${LESHY2_COMMON_DIR}/src/l2ip.c"
        "${LESHY2_COMMON_DIR}/src/high_speed_adapter.c"
        "${LESHY2_COMMON_DIR}/src/receiver_core.c"
        "${LESHY2_COMMON_DIR}/src/safety_core.c"
        "${LESHY2_COMMON_DIR}/src/system_model.c"
        "${LESHY2_COMMON_DIR}/src/update_core.c"
        "${LESHY2_GENERATED_HW_DIR}/src/c5_bsp.c"
    INCLUDE_DIRS
        "${LESHY2_COMMON_DIR}/include"
        "${LESHY2_GENERATED_HW_DIR}/include"
)

target_compile_options(${COMPONENT_LIB} PRIVATE
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
    "-ffile-prefix-map=${PROJECT_DIR}=."
    "-fdebug-prefix-map=${PROJECT_DIR}=."
)
