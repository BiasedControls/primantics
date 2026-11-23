# Minimal Imath config shim for Kit usd-release (headers + import lib only).
if(NOT TARGET Imath::Imath)

    add_library(Imath::Imath SHARED IMPORTED)
    add_library(Imath::ImathConfig INTERFACE IMPORTED)
    set_target_properties(Imath::Imath PROPERTIES
        IMPORTED_IMPLIB "${_KIT110_USD_ROOT}/lib/Imath-3_1.lib"
        IMPORTED_LOCATION "${_KIT110_USD_ROOT}/bin/Imath-3_1.dll"
        INTERFACE_INCLUDE_DIRECTORIES "${_KIT110_USD_ROOT}/include"
    )
endif()
