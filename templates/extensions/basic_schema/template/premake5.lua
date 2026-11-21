-- Use folder name to build extension name and tag. Version is specified explicitly.
local ext = get_current_extension_info()

project_ext (ext)
local schema = "{{ schema_name }}"
local schema_py = "{{ schema_python_module }}"
local install_root = "%{root}/_install/"..schema

repo_build.prebuild_link {
    { "data", ext.target_dir.."/data" },
    { "docs", ext.target_dir.."/docs" },
    { "{{ python_module_toplevel }}", ext.target_dir.."/{{ python_module_toplevel }}" },
}

-- Only the schema pieces the runtime needs: native lib, python module, plugInfo.
repo_build.prebuild_copy {
    { install_root.."/bin/**",        ext.target_dir.."/bin" },   -- windows-x86_64
    { install_root.."/lib/**",        ext.target_dir.."/lib" },   -- linux-x86_64
    { install_root.."/"..schema_py.."/**", ext.target_dir.."/"..schema_py },
    { install_root.."/plugins/**",    ext.target_dir.."/plugins" },
}