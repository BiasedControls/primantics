# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
import carb
import omni.ext
from omni.kit.viewport.utility import get_active_viewport_window
from .window import StartWindow

class MyExtension(omni.ext.IExt):
    def on_startup(self, ext_id: str):
        """This is called every time the extension is activated."""
        self._start_widget = None

        vp = get_active_viewport_window()
        if not vp:
            carb.log_error("Failed to get active viewport window")
            return

        self._start_widget = StartWindow(viewport=vp, ext_id=ext_id)


    def on_shutdown(self):
        """This is called every time the extension is deactivated. It is used
        to clean up the extension state."""
        if self._start_widget:
            self._start_widget.destroy()
