# Kit 110: Python 3.12 from repo build, OpenUSD 25.11 dev package from packman.
set(PXR_OPENUSD_PYTHON_DIR "${CMAKE_CURRENT_LIST_DIR}/../_build/target-deps/python")
set(Python3_ROOT_DIR "${PXR_OPENUSD_PYTHON_DIR}")
set(Python3_EXECUTABLE "${PXR_OPENUSD_PYTHON_DIR}/python.exe")
set(Python3_FIND_REGISTRY NEVER)
list(APPEND CMAKE_PREFIX_PATH
    "${CMAKE_CURRENT_LIST_DIR}/../_build/usd-deps/usd"
    "${CMAKE_CURRENT_LIST_DIR}/../_build/usd-deps/usd/lib/cmake"
    "${CMAKE_CURRENT_LIST_DIR}/../tools/build/cmake/kit110"
)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/../tools/build/cmake")
