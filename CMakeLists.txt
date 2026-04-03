cmake_minimum_required(VERSION 3.16)
project(CppCalculator VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

option(BUILD_TESTS    "Build unit tests"     ON)
option(BUILD_COVERAGE "Enable code coverage" OFF)

if(BUILD_COVERAGE)
    add_compile_options(--coverage -O0 -g)
    add_link_options(--coverage)
endif()

# ── Library
add_library(calculator_lib STATIC src/calculator.cpp)
target_include_directories(calculator_lib PUBLIC include)

# ── App
add_executable(calculator_app src/main.cpp)
target_link_libraries(calculator_app PRIVATE calculator_lib)

# ── Tests
if(BUILD_TESTS)
    include(FetchContent)
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG        v1.14.0
    )
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)

    enable_testing()

    add_executable(test_calculator tests/test_calculator.cpp)
    target_link_libraries(test_calculator PRIVATE calculator_lib GTest::gtest_main)
    target_include_directories(test_calculator PRIVATE include)

    include(GoogleTest)
    gtest_discover_tests(test_calculator
        OUTPUT_DIR ${CMAKE_BINARY_DIR}/test-results
        XML_OUTPUT_DIR ${CMAKE_BINARY_DIR}/test-results
    )
endif()

install(TARGETS calculator_app DESTINATION bin)
install(TARGETS calculator_lib DESTINATION lib)
install(FILES include/calculator.h DESTINATION include)
