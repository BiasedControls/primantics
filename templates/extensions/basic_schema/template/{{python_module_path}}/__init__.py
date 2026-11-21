# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import os
from pxr import Plug, UsdGeom

# Schema inherits UsdGeom.Xform, so we need to load it here to avoid this error
# "Failed to import python module TestSchema from \_build\windows-x86_64\release\exts\[schema].
# Error: extension class wrapper for base class class
# pxrInternal_v0_25_11__pxrReserved__::UsdGeomXform has not been created yet
_ = UsdGeom

# Resolve the extension root from this module's location.
_EXT_NAME = "{{ extension_name }}"
_SCHEMA_NAME = "{{ schema_name }}"
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_EXT_ROOT = os.path.abspath(os.path.join(_MODULE_DIR, *([os.pardir] * (_EXT_NAME.count(".") + 1))))

Plug.Registry().RegisterPlugins(os.path.join(_EXT_ROOT, "plugins", _SCHEMA_NAME, "resources"))

from .extension import *
