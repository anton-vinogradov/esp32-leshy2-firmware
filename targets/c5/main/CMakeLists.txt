idf_component_register(
    SRCS "app_main.c"
    INCLUDE_DIRS "."
    # IDF 6 exposes SPIRAM Kconfig only when this component is in the build.
    # esp_system's CONFIG_SPIRAM-dependent optional dependency cannot bootstrap it.
    PRIV_REQUIRES esp_system esp_psram log leshy2_portable
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
