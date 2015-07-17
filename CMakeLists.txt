cmake_minimum_required(VERSION 2.8.0)
project(libbot)

include(ExternalProject)

set(common_flags -DCMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX})

ExternalProject_Add(bot2-core 
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-core 
	CMAKE_ARGS ${common_flags})

ExternalProject_Add(bot2-vis 
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-vis 
	CMAKE_ARGS ${common_flags} bot2-core)

ExternalProject_Add(bot2-procman 
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-procman 
	CMAKE_ARGS ${common_flags})

ExternalProject_Add(bot2-lcmgl 
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-lcmgl 
	CMAKE_ARGS ${common_flags} bot2-vis)  

ExternalProject_Add(bot2-lcm-utils 
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-lcm-utils 
	CMAKE_ARGS ${common_flags})

ExternalProject_Add(bot2-param 
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-param 
	CMAKE_ARGS ${common_flags} bot2-core)

ExternalProject_Add(bot2-frames 
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-frames 
	CMAKE_ARGS ${common_flags}
	DEPENDS bot2-core bot2-param bot2-vis)
