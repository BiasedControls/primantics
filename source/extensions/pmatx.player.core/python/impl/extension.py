## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.ext
from .._pmatx_player_core_lib import *


# Use the extension entry points to acquire and release the interface.
class ExamplePybindExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()

    def on_startup(self):
        pass

    def on_shutdown(self):
        pass
