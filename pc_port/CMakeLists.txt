cmake_minimum_required(VERSION 3.24)
project(Galaxy2Coop LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------- options
set(G2C_DOL "${CMAKE_CURRENT_SOURCE_DIR}/../orig/SB4E01/sys/main.dol" CACHE FILEPATH
    "Path to YOUR OWN SMG2 (SB4E01) main.dol; lifted at build time, never committed")
set(G2C_LIFT_UNITS "MSL_C,Runtime" CACHE STRING
    "Unit prefixes (from config/SB4E01/splits.txt) to lift, or ALL for the whole executable")
set(G2C_LIFT_ALSO "strlen" CACHE STRING "Extra function names to lift (comma-separated)")
set(G2C_SHARDS 8 CACHE STRING "Number of generated C++ shards")

set(G2C_REPO_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/..")
set(G2C_SYMBOLS "${G2C_REPO_ROOT}/config/SB4E01/symbols.txt")
set(G2C_SPLITS "${G2C_REPO_ROOT}/config/SB4E01/splits.txt")

# ---------------------------------------------------------------- dependencies
include(FetchContent)
set(SDL_SHARED OFF CACHE BOOL "" FORCE)
set(SDL_STATIC ON CACHE BOOL "" FORCE)
set(SDL_TEST_LIBRARY OFF CACHE BOOL "" FORCE)
FetchContent_Declare(SDL3
    GIT_REPOSITORY https://github.com/libsdl-org/SDL.git
    GIT_TAG release-3.2.10
    GIT_SHALLOW TRUE)
FetchContent_Declare(imgui
    GIT_REPOSITORY https://github.com/ocornut/imgui.git
    GIT_TAG v1.91.9
    GIT_SHALLOW TRUE)
FetchContent_MakeAvailable(SDL3 imgui)

add_library(imgui STATIC
    ${imgui_SOURCE_DIR}/imgui.cpp
    ${imgui_SOURCE_DIR}/imgui_demo.cpp
    ${imgui_SOURCE_DIR}/imgui_draw.cpp
    ${imgui_SOURCE_DIR}/imgui_tables.cpp
    ${imgui_SOURCE_DIR}/imgui_widgets.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_sdl3.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_sdlrenderer3.cpp)
target_include_directories(imgui PUBLIC ${imgui_SOURCE_DIR} ${imgui_SOURCE_DIR}/backends)
target_link_libraries(imgui PUBLIC SDL3::SDL3-static)

# ---------------------------------------------------------------- runtime
add_library(g2c_runtime STATIC
    runtime/dispatch.cpp
    runtime/dol.cpp)
target_include_directories(g2c_runtime PUBLIC runtime)
if(MSVC)
    target_compile_options(g2c_runtime PUBLIC /utf-8 /permissive- /W3)
endif()

# ---------------------------------------------------------------- lifted code
find_package(Python3 COMPONENTS Interpreter REQUIRED)
set(G2C_RECOMP_DIR "${CMAKE_BINARY_DIR}/recomp")
if(EXISTS "${G2C_DOL}")
    set(G2C_RECOMP_OUT "${G2C_RECOMP_DIR}/recomp_decls.hpp" "${G2C_RECOMP_DIR}/recomp_register.cpp")
    set(G2C_RECOMP_SRCS "${G2C_RECOMP_DIR}/recomp_register.cpp")
    math(EXPR _last "${G2C_SHARDS} - 1")
    foreach(i RANGE 0 ${_last})
        if(i LESS 10)
            set(_n "0${i}")
        else()
            set(_n "${i}")
        endif()
        list(APPEND G2C_RECOMP_OUT "${G2C_RECOMP_DIR}/recomp_funcs_${_n}.cpp")
        list(APPEND G2C_RECOMP_SRCS "${G2C_RECOMP_DIR}/recomp_funcs_${_n}.cpp")
    endforeach()
    add_custom_command(
        OUTPUT ${G2C_RECOMP_OUT}
        COMMAND ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/tools/dol2cpp.py"
            --dol "${G2C_DOL}" --symbols "${G2C_SYMBOLS}" --splits "${G2C_SPLITS}"
            --units "${G2C_LIFT_UNITS}" --also "${G2C_LIFT_ALSO}"
            --out "${G2C_RECOMP_DIR}" --shards ${G2C_SHARDS}
        DEPENDS "${G2C_DOL}" "${G2C_SYMBOLS}" "${G2C_SPLITS}" "${CMAKE_CURRENT_SOURCE_DIR}/tools/dol2cpp.py"
        COMMENT "Lifting main.dol (${G2C_LIFT_UNITS}) to C++"
        VERBATIM)
    if(MSVC)
        set_source_files_properties(${G2C_RECOMP_SRCS} PROPERTIES COMPILE_OPTIONS "/O1;/bigobj")
    endif()
    message(STATUS "Galaxy2Coop: lifting ${G2C_DOL} (units: ${G2C_LIFT_UNITS})")
else()
    set(G2C_RECOMP_SRCS src/recomp_stub.cpp)
    message(WARNING "Galaxy2Coop: G2C_DOL not found (${G2C_DOL}); building without lifted code")
endif()

# ---------------------------------------------------------------- executable
add_executable(Galaxy2Coop
    src/main.cpp
    src/launcher.cpp
    src/smoke_test.cpp
    ${G2C_RECOMP_SRCS})
target_include_directories(Galaxy2Coop PRIVATE src "${G2C_RECOMP_DIR}")
target_link_libraries(Galaxy2Coop PRIVATE g2c_runtime imgui SDL3::SDL3-static)
if(MSVC)
    set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT Galaxy2Coop)
endif()
