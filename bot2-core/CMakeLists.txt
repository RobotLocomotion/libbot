cmake_minimum_required(VERSION 2.6.0)
cmake_policy(SET CMP0045 OLD)

set(POD_NAME bot2-core)

include(cmake/pods.cmake)

include(cmake/lcmtypes.cmake)
lcmtypes_build(C_AGGREGATE_HEADER bot_core.h CPP_AGGREGATE_HEADER bot_core.hpp)

add_subdirectory(src/bot_core)
add_subdirectory(java)
