add_definitions(-std=gnu99)

set(c_files lcmgl_decode.c)
set(h_files lcmgl_decode.h)
set(REQUIRED_LIBS)

if (USE_BOT_VIS)
  list(APPEND c_files lcmgl_bot_renderer.c)
  list(APPEND h_files lcmgl_bot_renderer.h)
  list(APPEND REQUIRED_LIBS bot2-vis gl)
  add_definitions(-DUSE_BOT_VIS)
endif()


add_library(bot2-lcmgl-renderer SHARED ${c_files})

find_package(OpenGL REQUIRED)
target_link_libraries(bot2-lcmgl-renderer ${OPENGL_LIBRARIES} lcmtypes_bot2-lcmgl)

if(REQUIRED_LIBS)
  pods_use_pkg_config_packages(bot2-lcmgl-renderer ${REQUIRED_LIBS})
endif()

list(APPEND REQUIRED_LIBS lcmtypes_bot2-lcmgl)


# set the library API version.  Increment this every time the public API
# changes.
set_target_properties(bot2-lcmgl-renderer PROPERTIES SOVERSION 1)

pods_install_libraries(bot2-lcmgl-renderer)

pods_install_headers(${h_files} DESTINATION bot_lcmgl_render)

pods_install_pkg_config_file(bot2-lcmgl-renderer
    LIBS -lbot2-lcmgl-renderer
    REQUIRES ${REQUIRED_LIBS}
    VERSION 0.0.1)
