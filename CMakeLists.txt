cmake_minimum_required(VERSION 2.8.5)
project(libbot)

# PODs out-of-source build logic
if (CMAKE_INSTALL_PREFIX STREQUAL "/usr/local" OR CMAKE_INSTALL_PREFIX STREQUAL "C:/Program Files/${PROJECT_NAME}")
  find_file(_build_dir build PATHS ${PROJECT_SOURCE_DIR} ${PROJECT_SOURCE_DIR}/.. ${PROJECT_SOURCE_DIR}/../.. ${PROJECT_SOURCE_DIR}/../../.. ${PROJECT_SOURCE_DIR}/../../../..)
  if (_build_dir)
      set(CMAKE_INSTALL_PREFIX "${_build_dir}" CACHE PATH "Install location for project" FORCE)
  else()
    execute_process(COMMAND ${CMAKE_COMMAND} -E make_directory ${PROJECT_SOURCE_DIR}/build)
    set(CMAKE_INSTALL_PREFIX ${PROJECT_SOURCE_DIR}/build)
  endif()
endif()
message(STATUS CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX})

# set a default build type if none was specified
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()


# Look for the gdkx.h header to decide whether the local gtk2 install has
# X11 support or not.
find_file(GDKX_HEADER gdkx.h PATH_SUFFIXES gtk-2.0/gdk)
if(GDKXHEADER)
  set(bot_vis_default ON)
  message(STATUS "gdkx.h found, system appears to have gtk+X11 support")
else()
  set(bot_vis_default OFF)
  message(STATUS "gdkx.h not found, system not appear to have gtk+X11 support")
endif()


option(WITH_BOT_VIS "Build with bot2-vis" ${bot_vis_default})


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
  BINARY_DIR ${PROJECT_SOURCE_DIR}/bot2-core/pod-build
  CMAKE_CACHE_ARGS ${default_cmake_args})
checkbuild(bot2-core)

ExternalProject_Add(bot2-procman
  SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-procman
  BINARY_DIR ${PROJECT_SOURCE_DIR}/bot2-procman/pod-build
  CMAKE_CACHE_ARGS ${default_cmake_args})
checkbuild(bot2-procman)

ExternalProject_Add(bot2-lcm-utils
  SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-lcm-utils
  BINARY_DIR ${PROJECT_SOURCE_DIR}/bot2-lcm-utils/pod-build
  CMAKE_CACHE_ARGS ${default_cmake_args})
checkbuild(bot2-lcm-utils)

ExternalProject_Add(bot2-param
  SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-param
  BINARY_DIR ${PROJECT_SOURCE_DIR}/bot2-param/pod-build
  CMAKE_CACHE_ARGS ${default_cmake_args}
  DEPENDS bot2-core)

if (WITH_BOT_VIS)

  message(STATUS "Configuring with bot2-vis, modules requiring gtk+x11 will be built.")

  ExternalProject_Add(bot2-vis
    SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-vis
    BINARY_DIR ${PROJECT_SOURCE_DIR}/bot2-vis/pod-build
    CMAKE_CACHE_ARGS ${default_cmake_args}
    DEPENDS bot2-core)

  ExternalProject_Add(bot2-lcmgl
    SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-lcmgl
    BINARY_DIR ${PROJECT_SOURCE_DIR}/bot2-lcmgl/pod-build
    CMAKE_CACHE_ARGS ${default_cmake_args} -DUSE_BOT_VIS:BOOL=${WITH_BOT_VIS}
    DEPENDS bot2-vis)

  ExternalProject_Add(bot2-frames
    SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-frames
    BINARY_DIR ${PROJECT_SOURCE_DIR}/bot2-frames/pod-build
    CMAKE_CACHE_ARGS ${default_cmake_args}
    DEPENDS bot2-core bot2-param bot2-vis bot2-lcmgl)

else()

  message(STATUS "Configuring without bot2-vis, modules requiring gtk+x11 will not be built.")

  ExternalProject_Add(bot2-lcmgl
    SOURCE_DIR ${PROJECT_SOURCE_DIR}/bot2-lcmgl
    BINARY_DIR ${PROJECT_SOURCE_DIR}/bot2-lcmgl/pod-build
    CMAKE_CACHE_ARGS ${default_cmake_args} -DUSE_BOT_VIS:BOOL=${WITH_BOT_VIS})

endif()
