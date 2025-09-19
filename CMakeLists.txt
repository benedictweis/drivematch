cmake_minimum_required(VERSION 3.10)
project(DriveMatch VERSION 0.0.1)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

file(GLOB ${PROJECT_NAME}_SRC CONFIGURE_DEPENDS "src/*.cpp")

file(GLOB ${PROJECT_NAME}_TEST CONFIGURE_DEPENDS "test/*.cpp")

include_directories(include)
include_directories(src)

add_executable(${PROJECT_NAME}Tests ${DriveMatch_TEST} ${DriveMatch_SRC})
target_include_directories(${PROJECT_NAME}Tests PRIVATE thirdparty/doctest)

include(CTest)
enable_testing()

add_test(NAME ${PROJECT_NAME}Tests COMMAND ${PROJECT_NAME}Tests)
