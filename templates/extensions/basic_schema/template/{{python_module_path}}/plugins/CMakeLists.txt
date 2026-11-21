set(CMAKE_INSTALL_PREFIX "${USD_SCHEMA_INSTALL_ROOT}/{{schema_name}}" CACHE PATH "Install prefix for {{schema_name}}" FORCE)
set(CMAKE_INSTALL_BINDIR "bin")
set(CMAKE_INSTALL_LIBDIR "lib")
set(CMAKE_INSTALL_INCLUDEDIR "include")

openusd_schema({{schema_name}}
    GENERATE_SCHEMA
    SCHEMA_FILE
        "${CMAKE_CURRENT_LIST_DIR}/schema.usda"
)

# TestBase inherits </Xform>, so generated code depends on usdGeom symbols.
if(TARGET usdGeom)
    target_link_libraries({{schema_name}} PUBLIC usdGeom)
    if(TARGET _{{schema_name}})
        target_link_libraries(_{{schema_name}} PUBLIC usdGeom)
    endif()
endif()
