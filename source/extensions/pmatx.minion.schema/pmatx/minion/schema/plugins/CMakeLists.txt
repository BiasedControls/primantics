set(CMAKE_INSTALL_PREFIX "${USD_SCHEMA_INSTALL_ROOT}/pmatxMinion" CACHE PATH "Install prefix for pmatxMinion" FORCE)
set(CMAKE_INSTALL_BINDIR "bin")
set(CMAKE_INSTALL_LIBDIR "lib")
set(CMAKE_INSTALL_INCLUDEDIR "include")

openusd_schema(pmatxMinion
    GENERATE_SCHEMA
    SCHEMA_FILE
        "${CMAKE_CURRENT_LIST_DIR}/schema.usda"
)

# TestBase inherits </Xform>, so generated code depends on usdGeom symbols.
if(TARGET usdGeom)
    target_link_libraries(pmatxMinion PUBLIC usdGeom)
    if(TARGET _pmatxMinion)
        target_link_libraries(_pmatxMinion PUBLIC usdGeom)
    endif()
endif()
