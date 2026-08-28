cmake_minimum_required(VERSION 3.16)

# This project has no registry-managed components; configure/build must stay offline.
set(ENV{IDF_COMPONENT_MANAGER} "0")
set(COMPONENTS main leshy2_portable leshy2_s3_c5)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(leshy2_s3)
