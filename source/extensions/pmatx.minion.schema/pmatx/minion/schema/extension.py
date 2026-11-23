# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES.
# All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from pathlib import Path
import carb
import omni.ext
import omni.kit.app

_EXT_NAME = "pmatx.minion.schema"
EXT_PATH = carb.tokens.get_tokens_interface().resolve("${" + _EXT_NAME + "}")


class MyExtension(omni.ext.IExt):
    """This is a blank extension template."""

    def __init__(self):
        super().__init__()
        self._hooks = []

    def on_startup(self, _ext_id):
        """This is called every time the extension is activated."""
        print("[pmatx.minion.schema] Extension startup")
        manager = omni.kit.app.get_app().get_extension_manager()
        self._hooks.append(
            manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self.register_icons(),
                on_disable_fn=None,
                ext_name="omni.kit.widget.stage",
                hook_name="pmatx/minion/schema stage extension listener",
            )
        )

    def register_icons(self):
        """Registers icons based on the SVG files found in the icons directory."""
        import omni.kit.widget.stage

        stage_icons = omni.kit.widget.stage.StageIcons()
        icon_path = Path(EXT_PATH).joinpath("pmatx/minion/schema/icons")

        # Read all the svg files in the directory
        icons = {icon.stem: str(icon) for icon in icon_path.glob("*.svg")}
        for prim_type, filename in icons.items():
            stage_icons.set(prim_type, filename)

    def on_shutdown(self):
        """This is called every time the extension is deactivated. It is used
        to clean up the extension state."""
        self._hooks.clear()
        print("[pmatx.minion.schema] Extension shutdown")
