-- Setup the extension.
local ext = get_current_extension_info()
project_ext(ext)

-- Link folders that should be packaged with the extension.
repo_build.prebuild_link {
    { "data", ext.target_dir.."/data" },
    { "docs", ext.target_dir.."/docs" },
}

-- Build the C++ plugin that will be loaded by the extension.
project_ext_plugin(ext, "pmatx.player.core.plugin")
    add_files("include", "include/pmatx/player/core")
    add_files("source", "plugins/pmatx.player.core")
    add_usd{"usdGeom", "usdPhysics"}
    includedirs {
        "include",
        "plugins/pmatx.player.core",
        "%{target_deps}/omni_physics/release/include"
    }

-- Build Python bindings that will be loaded by the extension.
project_ext_bindings {
    ext = ext,
    project_name = "pmatx.player.core.python",
    module = "_pmatx_player_core_lib",
    src = "bindings/python/pmatx.player.core",
    target_subdir = "pmatx/player/core"
}
    includedirs { "include" }
    repo_build.prebuild_link {
        { "python/impl", ext.target_dir.."/pmatx/player/core/impl" },
        { "python/tests", ext.target_dir.."/pmatx/player/core/tests" },
    }

-- Build the C++ plugin that will be loaded by the tests.
project_ext_tests(ext, "pmatx.player.core.tests")
    add_files("source", "plugins/pmatx.player.core.tests")
    includedirs { "include", "plugins/pmatx.player.core.tests", "%{target_deps}/doctest/include" }
