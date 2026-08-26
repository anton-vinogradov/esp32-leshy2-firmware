idf_component_register(
    SRCS
        "s3_c5_fake.c"
        "s3_c5_host.c"
    INCLUDE_DIRS "include"
    REQUIRES
        esp_driver_sdmmc
        esp_serial_slave_link
        leshy2_portable
        sdmmc
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
