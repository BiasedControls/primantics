# Use the USD and Python packages selected together by the Kit SDK.
set(_KIT110_USD_ROOT "${REPO_ROOT}/_build/target-deps/usd/release")
if(NOT EXISTS "${_KIT110_USD_ROOT}/pxrConfig.cmake")
    message(FATAL_ERROR "Missing ${_KIT110_USD_ROOT}/pxrConfig.cmake. Run repo.bat build from the repo root first.")
endif()
set(pxr_DIR "${_KIT110_USD_ROOT}")
set(MaterialX_DIR "${_KIT110_USD_ROOT}/lib/cmake/MaterialX")
set(PXR_OPENUSD_PYTHON_DIR "${CMAKE_CURRENT_LIST_DIR}/../_build/target-deps/python")
set(Python3_ROOT_DIR "${PXR_OPENUSD_PYTHON_DIR}")
set(Python3_EXECUTABLE "${PXR_OPENUSD_PYTHON_DIR}/python.exe")
set(Python3_FIND_REGISTRY NEVER)
list(PREPEND CMAKE_PREFIX_PATH
    "${_KIT110_USD_ROOT}"
    "${_KIT110_USD_ROOT}/lib/cmake"
    "${CMAKE_CURRENT_LIST_DIR}/../tools/build/cmake/kit110"
)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/../tools/build/cmake")
