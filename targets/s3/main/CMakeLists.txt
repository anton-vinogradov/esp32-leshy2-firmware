idf_component_register(
    SRCS "app_main.c"
    INCLUDE_DIRS "."
    PRIV_REQUIRES esp_system log leshy2_portable leshy2_s3_c5
)

target_compile_options(${COMPONENT_LIB} PRIVATE
    -std=c17
    -Wall
    -Wextra
    -Werror
    -Wformat=2
    -Wshadow
    -Wundef
    -ffunction-sections
    -fdata-sections
    -fstack-usage
    "-ffile-prefix-map=${PROJECT_DIR}=."
    "-fdebug-prefix-map=${PROJECT_DIR}=."
)
