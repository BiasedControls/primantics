# Minimal TBB config shim for Kit usd-release (headers + import lib only).
if(NOT TARGET TBB::tbb)

    add_library(TBB::tbb SHARED IMPORTED)
    set_target_properties(TBB::tbb PROPERTIES
        INTERFACE_COMPILE_DEFINITIONS "$<$<CONFIG:Debug>:TBB_USE_DEBUG=1>"
        INTERFACE_INCLUDE_DIRECTORIES "${_KIT110_USD_ROOT}/include/tbb"
        INTERFACE_SYSTEM_INCLUDE_DIRECTORIES "${_KIT110_USD_ROOT}/include/tbb"
        IMPORTED_IMPLIB "${_KIT110_USD_ROOT}/lib/tbb12.lib"
        IMPORTED_IMPLIB_RELEASE "${_KIT110_USD_ROOT}/lib/tbb12.lib"
        IMPORTED_IMPLIB_DEBUG "${_KIT110_USD_ROOT}/lib/tbb12.lib"
        IMPORTED_IMPLIB_RELWITHDEBINFO "${_KIT110_USD_ROOT}/lib/tbb12.lib"
        IMPORTED_IMPLIB_MINSIZEREL "${_KIT110_USD_ROOT}/lib/tbb12.lib"
        IMPORTED_LOCATION "${_KIT110_USD_ROOT}/bin/tbb12.dll"
        IMPORTED_LOCATION_RELEASE "${_KIT110_USD_ROOT}/bin/tbb12.dll"
        IMPORTED_LOCATION_DEBUG "${_KIT110_USD_ROOT}/bin/tbb12.dll"
        IMPORTED_LOCATION_RELWITHDEBINFO "${_KIT110_USD_ROOT}/bin/tbb12.dll"
        IMPORTED_LOCATION_MINSIZEREL "${_KIT110_USD_ROOT}/bin/tbb12.dll"
        MAP_IMPORTED_CONFIG_RELWITHDEBINFO Release
    )
endif()
