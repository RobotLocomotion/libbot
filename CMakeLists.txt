cmake_minimum_required(VERSION 2.8.5)
project(libbot)

# set a default build type if none was specified
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

option(WITH_BOT_VIS "Build with bot2-vis" OFF)

# call this macro for each project without dependencies so that it will
# re-check the build in case there are modified files.  In CMake 3.1, you
# can use the BUILD_ALWAYS flag instead, but this is for support of older
# version of cmake.
macro(checkbuild proj)
	ExternalProject_Add_Step(${proj} forceconfigure
			COMMAND ${CMAKE_COMMAND} -E echo "Check build of ${proj}"
			DEPENDEES configure
			DEPENDERS build
			ALWAYS 1)
endmacro()

include(ExternalProject)

# pass thru certain cmake variables.
set(default_cmake_args
  "-DCMAKE_PREFIX_PATH:PATH=${CMAKE_INSTALL_PREFIX};${CMAKE_PREFIX_PATH}"
  "-DCMAKE_INSTALL_PREFIX:PATH=${CMAKE_INSTALL_PREFIX}"
  "-DCMAKE_BUILD_TYPE:STRING=${CMAKE_BUILD_TYPE}"
  )


ExternalProject_Add(bot2-core
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-core
	CMAKE_CACHE_ARGS ${default_cmake_args})
checkbuild(bot2-core)

ExternalProject_Add(bot2-procman
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-procman
	CMAKE_CACHE_ARGS ${default_cmake_args})
checkbuild(bot2-procman)

ExternalProject_Add(bot2-lcm-utils
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-lcm-utils
	CMAKE_CACHE_ARGS ${default_cmake_args})
checkbuild(bot2-lcm-utils)

ExternalProject_Add(bot2-param
	SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-param
	CMAKE_CACHE_ARGS ${default_cmake_args}
  DEPENDS bot2-core)

if (WITH_BOT_VIS)

  ExternalProject_Add(bot2-vis
	  SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-vis
	  CMAKE_CACHE_ARGS ${default_cmake_args}
    DEPENDS bot2-core)

  ExternalProject_Add(bot2-lcmgl
	  SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-lcmgl
	  CMAKE_CACHE_ARGS ${default_cmake_args} -DUSE_BOT_VIS:BOOL=${WITH_BOT_VIS}
    DEPENDS bot2-vis)

  ExternalProject_Add(bot2-frames
	  SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-frames
	  CMAKE_CACHE_ARGS ${default_cmake_args}
	  DEPENDS bot2-core bot2-param bot2-vis bot2-lcmgl)

else()

  ExternalProject_Add(bot2-lcmgl
	  SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-lcmgl
	  CMAKE_CACHE_ARGS ${default_cmake_args} -DUSE_BOT_VIS:BOOL=${WITH_BOT_VIS})

endif()
