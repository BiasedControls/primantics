// Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#include <carb/BindingsPythonUtils.h>


CARB_BINDINGS("pmatx.player.core.python")

// DISABLE_PYBIND11_DYNAMIC_CAST(pmatx::player::core::IPmatxPlayerCoreInterface)
// DISABLE_PYBIND11_DYNAMIC_CAST(pmatx::player::core::IPmatxPlayerCoreObjectInterface)

// Define the pybind11 module using the same name specified in premake5.lua
PYBIND11_MODULE(_pmatx_player_core_lib, m)
{
}
