cmake_minimum_required(VERSION 3.20)
project(DriveMatch VERSION 0.0.1 LANGUAGES CXX)

# --- Global settings ---
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF) # portable standard C++ only

# --- Dependencies ---
include(FetchContent)

# doctest
FetchContent_Declare(
    doctest
    GIT_REPOSITORY https://github.com/doctest/doctest.git
    GIT_TAG v2.4.12
)
FetchContent_MakeAvailable(doctest)

# SQLiteCpp
FetchContent_Declare(
    SQLiteCpp
    GIT_REPOSITORY https://github.com/SRombauts/SQLiteCpp.git
    GIT_TAG 3.3.3
)
FetchContent_MakeAvailable(SQLiteCpp)

# nlohmann_json
FetchContent_Declare(json URL https://github.com/nlohmann/json/releases/download/v3.12.0/json.tar.xz)
FetchContent_MakeAvailable(json)

# Qt
find_package(Qt6 6.9 REQUIRED COMPONENTS Widgets)

# --- Sources ---
file(GLOB_RECURSE PROJECT_SOURCES CONFIGURE_DEPENDS "src/*.cpp")
file(GLOB_RECURSE PROJECT_HEADERS CONFIGURE_DEPENDS "include/*.hpp")

file(GLOB_RECURSE TEST_SOURCES CONFIGURE_DEPENDS "test/*.cpp")

file(GLOB_RECURSE DESKTOP_SOURCES CONFIGURE_DEPENDS "desktop/*.cpp")

# --- Targets ---
# Main library
add_library(${PROJECT_NAME} STATIC
    ${PROJECT_SOURCES}
    ${PROJECT_HEADERS}
)
target_include_directories(${PROJECT_NAME}
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include> # for installation
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_link_libraries(${PROJECT_NAME}
    PUBLIC
        SQLiteCpp
        Qt6::Widgets
        nlohmann_json::nlohmann_json
)

# Test executable
add_executable(${PROJECT_NAME}Tests ${TEST_SOURCES})
target_link_libraries(${PROJECT_NAME}Tests
    PRIVATE
        ${PROJECT_NAME}
        doctest::doctest
)

target_include_directories(${PROJECT_NAME}Tests
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Desktop application
add_executable(${PROJECT_NAME}Desktop ${DESKTOP_SOURCES})
target_link_libraries(${PROJECT_NAME}Desktop
    PRIVATE
        ${PROJECT_NAME}
        Qt6::Widgets
)

# --- Testing ---
include(CTest)
enable_testing()
add_test(NAME ${PROJECT_NAME}Tests COMMAND ${PROJECT_NAME}Tests)
