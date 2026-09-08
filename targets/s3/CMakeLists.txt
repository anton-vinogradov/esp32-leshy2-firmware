cmake_minimum_required(VERSION 3.16)

# This project has no registry-managed components; configure/build must stay offline.
set(ENV{IDF_COMPONENT_MANAGER} "0")
set(COMPONENTS main leshy2_portable leshy2_s3_c5)
get_filename_component(LESHY2_REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
# PROJECT_DIR alone misses common/ and generated/r2/ outside this target root.
add_compile_options(
    "-ffile-prefix-map=${LESHY2_REPO_ROOT}=."
    "-fdebug-prefix-map=${LESHY2_REPO_ROOT}=."
)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(leshy2_s3)

# Validate resolved Kconfig, not just the requested sdkconfig.defaults text.
# This runs after IDF has expanded component dependencies and generated sdkconfig.
idf_build_get_property(LESHY2_S3_SDKCONFIG SDKCONFIG)
idf_build_get_property(LESHY2_S3_COMPONENTS BUILD_COMPONENTS)
idf_build_get_property(LESHY2_S3_PYTHON PYTHON)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/verify_memory_config.py"
    "${LESHY2_REPO_ROOT}/config/sdkconfig.defaults.esp32s3"
)
execute_process(
    COMMAND "${LESHY2_S3_PYTHON}" "${CMAKE_CURRENT_SOURCE_DIR}/verify_memory_config.py"
        --sdkconfig "${LESHY2_S3_SDKCONFIG}"
        --components ${LESHY2_S3_COMPONENTS}
    RESULT_VARIABLE LESHY2_S3_MEMORY_RESULT
    OUTPUT_VARIABLE LESHY2_S3_MEMORY_OUTPUT
    ERROR_VARIABLE LESHY2_S3_MEMORY_ERROR
)
if(NOT LESHY2_S3_MEMORY_RESULT EQUAL 0)
    message(FATAL_ERROR "S3 memory contract rejected:\n${LESHY2_S3_MEMORY_OUTPUT}${LESHY2_S3_MEMORY_ERROR}")
endif()
message(STATUS "${LESHY2_S3_MEMORY_OUTPUT}")
