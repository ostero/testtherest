cmake_minimum_required(VERSION 3.14)
project(RESTServer)

# Set compiler and standard
set(CMAKE_CXX_COMPILER "g++")
set(CMAKE_CXX_STANDARD 17)

# Include directory for httplib.h
include_directories(include/third-party)

# Source file
set(SOURCES src/main.cpp)

# Add executable
add_executable(RESTServer ${SOURCES})

target_link_libraries(RESTServer  pthread)
