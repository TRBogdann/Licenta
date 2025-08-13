cmake_minimum_required(VERSION 3.10)
project(DESKTOP_APP)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add program_main.cpp and all other source files
set(SOURCES
    program.cpp
    ./controls/controls.cpp
    ./tools/tools.cpp
    ./slicer/slicer.cpp
)

# Create the executable
add_executable(program ${SOURCES})

# Find OpenGL and pkg-config
find_package(OpenGL REQUIRED)
find_package(PkgConfig REQUIRED)
pkg_check_modules(GLEW REQUIRED glew)
pkg_check_modules(GLFW REQUIRED glfw3)
find_library(GAMEENGINE_LIBRARY gameengine PATHS /usr/lib REQUIRED)

# Include directories (from pkg-config)
include_directories(
    ${GLEW_INCLUDE_DIRS}
    ${GLFW_INCLUDE_DIRS}
)

# Link libraries
target_link_libraries(program
    imgui
    ${GLEW_LIBRARIES}
    ${GLFW_LIBRARIES}
    EGL
    OpenGL::GL
    ${GAMEENGINE_LIBRARY}
)




