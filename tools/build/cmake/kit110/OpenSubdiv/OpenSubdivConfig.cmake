# Minimal OpenSubdiv config shim (schema build does not use OSD directly).
add_library(OpenSubdiv::osdCPU SHARED IMPORTED)
add_library(OpenSubdiv::osdGPU SHARED IMPORTED)
