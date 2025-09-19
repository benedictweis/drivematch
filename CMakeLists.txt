cmake_minimum_required(VERSION 3.12)
project(DriveMatch VERSION 0.0.1)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

file(GLOB DriveMatch_SRC CONFIGURE_DEPENDS "src/*.cpp")

file(GLOB DriveMatch_TESTS CONFIGURE_DEPENDS "test/*.cpp")

include_directories(include)
include_directories(src)

add_executable(DriveMatchTests ${DriveMatch_TESTS} ${DriveMatch_SRC})

include(CTest)
enable_testing()

add_test(NAME DriveMatchTests COMMAND DriveMatchTests)