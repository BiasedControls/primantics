# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Single-schema build harness.
#
# CMAKE_INSTALL_PREFIX is a project-wide variable, so two schemas cannot share
# one CMake project without their install rules colliding under a single
# prefix. Instead, schema/scripts/build_schemas.py invokes this project once
# per discovered schema, passing the plugin directory in SCHEMA_PLUGIN_DIR
# and the per-schema CMAKE_INSTALL_PREFIX on the command line.
#
# You can also invoke this project directly to build a single schema:
#     cmake -S schema/ -B _build/cmake/<name>/ \
#           -DSCHEMA_PLUGIN_DIR=<repo>/source/extensions/<ext>/<...>/plugins \
#           -DCMAKE_INSTALL_PREFIX=<repo>/_install/<name>
#
cmake_minimum_required(VERSION 3.23.1)

get_filename_component(REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)

if(NOT DEFINED SCHEMA_PLUGIN_DIR OR NOT EXISTS "${SCHEMA_PLUGIN_DIR}/CMakeLists.txt")
    message(FATAL_ERROR
        "SCHEMA_PLUGIN_DIR must point to a schema plugin directory containing "
        "CMakeLists.txt (got '${SCHEMA_PLUGIN_DIR}'). "
        "Run schema/build.bat (which invokes schema/scripts/build_schemas.py) "
        "to discover and build all schemas, or pass -DSCHEMA_PLUGIN_DIR=... "
        "manually to build a single schema."
    )
endif()

# Retained for compatibility with per-schema plugins/CMakeLists.txt files
# that reference ${USD_SCHEMA_INSTALL_ROOT}/<schemaName>.
set(USD_SCHEMA_INSTALL_ROOT "${REPO_ROOT}/_install" CACHE PATH "Root for per-schema installs")

# Avoid CMake's default "C:/Program Files (x86)/usd-plugins" install path on
# Windows if the caller forgot to pass -DCMAKE_INSTALL_PREFIX.
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX "${USD_SCHEMA_INSTALL_ROOT}" CACHE PATH "Install root" FORCE)
endif()

project(usd-plugin CXX)

if (MSVC)
    # /MP: compile a target's source files in parallel (MSBuild is serial per project otherwise).
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /FS /MP")
endif()

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})
include(PackmanDeps)
include(NvPxrPlugin)

if (PXR_VERSION LESS_EQUAL 2311)
    set(CMAKE_CXX_STANDARD 14)
else()
    set(CMAKE_CXX_STANDARD 17)
endif()

# Derive schema name from libraryName in schema.usda (fallback: plugin folder
# name) purely so the CMake binary sub-dir has a stable, human-readable tag.
set(_usda_file "${SCHEMA_PLUGIN_DIR}/schema.usda")
if(EXISTS "${_usda_file}")
    file(READ "${_usda_file}" _usda_contents)
    string(REGEX MATCH "libraryName[ \t]*=[ \t]*\"([^\"]+)\"" _match "${_usda_contents}")
    unset(_usda_contents)
    unset(_match)
endif()
if(CMAKE_MATCH_1)
    set(schema_name "${CMAKE_MATCH_1}")
else()
    get_filename_component(schema_name "${SCHEMA_PLUGIN_DIR}" NAME)
endif()

message(STATUS "Building schema '${schema_name}' from ${SCHEMA_PLUGIN_DIR}")
message(STATUS "Installing to ${CMAKE_INSTALL_PREFIX}")

add_subdirectory("${SCHEMA_PLUGIN_DIR}" "${CMAKE_BINARY_DIR}/${schema_name}")
