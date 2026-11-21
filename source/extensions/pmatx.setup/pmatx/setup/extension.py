# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import asyncio
import inspect
import logging
import os
import platform
import subprocess
import sys
import webbrowser
from pathlib import Path


import carb
import carb.settings
import carb.tokens
import omni.ext
import omni.kit.app
import omni.kit.menu.utils
import omni.kit.stage_templates as stage_templates
import omni.kit.window.property as property_window_ext
import omni.ui as ui
import omni.usd
from omni.kit.menu.utils import MenuLayout, MenuItemDescription
from omni.kit.property.usd import PrimPathWidget
from omni.kit.quicklayout import QuickLayout
from omni.kit.window.title import get_main_window_title

DATA_PATH = Path(carb.tokens.get_tokens_interface().resolve(
    "${pmatx.setup}")
)


async def _load_layout(layout_file: str, keep_windows_open=False):
    """Loads a provided layout file and ensures the viewport is set to FILL."""
    try:
        # few frames delay to avoid the conflict with the
        # layout of omni.kit.mainwindow
        for _ in range(3):
            await omni.kit.app.get_app().next_update_async()
        QuickLayout.load_file(layout_file, keep_windows_open)
    except:
        QuickLayout.load_file(layout_file)


class CreateSetupExtension(omni.ext.IExt):
    """Create Final Configuration"""

    def on_startup(self, _ext_id):
        """
        setup the window layout, menu, final configuration
        of the extensions etc
        """
        self._settings = carb.settings.get_settings()
        if self._settings and self._settings.get("/app/warmupMode"):
            # if warmup mode is enabled, we don't want to load the stage or
            # layout, just return
            return

        self._menu_layout = []

        telemetry_logger = logging.getLogger("idl.telemetry.opentelemetry")
        telemetry_logger.setLevel(logging.ERROR)

        # this is a work around as some Extensions don't properly setup their
        # default setting in time
        self._set_defaults()

        # adjust couple of viewport settings
        self._settings.set("/app/viewport/boundingBoxes/enabled", True)

        # These two settings do not co-operate well on ADA cards, so for
        # now simulate a toggle of the present thread on startup to work around
        if self._settings.get("/exts/omni.kit.renderer.core/present/enabled") \
            and self._settings.get(
            "/exts/omni.kit.widget.viewport/autoAttach/mode"
        ):
            async def _toggle_present(settings, n_waits: int = 1):
                async def _toggle_setting(app, enabled: bool, n_waits: int):
                    for _ in range(n_waits):
                        await app.next_update_async()
                    settings.set(
                        "/exts/omni.kit.renderer.core/present/enabled",
                        enabled
                    )

                app = omni.kit.app.get_app()
                await _toggle_setting(app, False, n_waits)
                await _toggle_setting(app, True, n_waits)

            asyncio.ensure_future(_toggle_present(self._settings))

        self._settings.set("persistent/app/useFabricSceneDelegate", True)
        self._settings.set("app/useFabricSceneDelegate", True)

        # Adjust the Window Title to show the Create Version
        window_title = get_main_window_title()

        app_version = self._settings.get("/app/version")
        if not app_version:
            with open(
                carb.tokens.get_tokens_interface().resolve("${app}/../VERSION"),
                encoding="utf-8"
            ) as f:
                app_version = f.read()

        if app_version:
            if "+" in app_version:
                app_version, _ = app_version.split("+")

            # for RC version we remove some details
            if self._settings.get("/privacy/externalBuild"):
                if "-" in app_version:
                    app_version, _ = app_version.split("-")
                window_title.set_app_version(app_version)
            else:
                window_title.set_app_version(app_version)

        imgui_style_applied = False
        try:
            # using imgui directly to adjust some color and Variable
            import omni.kit.imgui as _imgui
            imgui = _imgui.acquire_imgui()
            if imgui.is_valid():
                imgui.push_style_color(_imgui.StyleColor.ScrollbarGrab, carb.Float4(0.4, 0.4, 0.4, 1))
                imgui.push_style_color(_imgui.StyleColor.ScrollbarGrabHovered, carb.Float4(0.6, 0.6, 0.6, 1))
                imgui.push_style_color(_imgui.StyleColor.ScrollbarGrabActive, carb.Float4(0.8, 0.8, 0.8, 1))
                imgui.push_style_var_float(_imgui.StyleVar.DockSplitterSize, 2)
                imgui_style_applied = True
        except ImportError:
            pass

        if not imgui_style_applied:
            carb.log_error("Style may not be as expected (carb.imgui was not valid)")

        layout_file = f"{DATA_PATH}/layouts/default.json"

        # Setting to hack few things in test run. Ideally we shouldn't need it.
        test_mode = self._settings.get("/app/testMode")

        if not test_mode:
            asyncio.ensure_future(_load_layout(layout_file, True))

        asyncio.ensure_future(self.__property_window())

        self.__menu_update()

        if not test_mode and not \
                self._settings.get("/app/content/emptyStageOnStart"):
            asyncio.ensure_future(self.__new_stage())

        startup_time = \
            omni.kit.app.get_app_interface().get_time_since_start_s()
        self._settings.set(
            "/crashreporter/data/startup_time", f"{startup_time}"
        )

    def _set_defaults(self):
        """
        This is trying to setup some defaults for extensions to avoid warnings.
        """
        self._settings.set_default("/persistent/app/omniverse/bookmarks", {})
        self._settings.set_default(
            "/persistent/app/stage/timeCodeRange", [0, 100]
        )

        self._settings.set_default(
            "/persistent/audio/context/closeAudioPlayerOnStop",
            False
        )

        self._settings.set_default(
            "/persistent/app/primCreation/PrimCreationWithDefaultXformOps",
            True
        )
        self._settings.set_default(
            "/persistent/app/primCreation/DefaultXformOpType",
            "Scale, Rotate, Translate"
        )
        self._settings.set_default(
            "/persistent/app/primCreation/DefaultRotationOrder",
            "ZYX"
        )
        self._settings.set_default(
            "/persistent/app/primCreation/DefaultXformOpPrecision",
            "Double"
        )

        # omni.kit.property.tagging
        self._settings.set_default(
            "/persistent/exts/omni.kit.property.tagging/showAdvancedTagView",
            False
        )
        self._settings.set_default(
            "/persistent/exts/omni.kit.property.tagging/showHiddenTags",
            False
        )
        self._settings.set_default(
            "/persistent/exts/omni.kit.property.tagging/modifyHiddenTags",
            False
        )

        self._settings.set_default(
            "/rtx/sceneDb/ambientLightIntensity", 0.0
        )  # set default ambientLight intensity to Zero

    async def __new_stage(self):
        """Create a new stage """
        # 5 frame delay to allow Layout
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()

        if omni.usd.get_context().can_open_stage() and not omni.usd.get_context().get_stage_url():
            stage_templates.new_stage(template=None)

    async def __property_window(self):
        """Creates a propety window and sets column sizes."""
        await omni.kit.app.get_app().next_update_async()

        property_window = property_window_ext.get_window()
        property_window.set_scheme_delegate_layout(
            "Create Layout",
            ["basis_curves_prim", "path_prim", "material_prim",
             "xformable_prim", "shade_prim", "camera_prim"],
        )

        # expand width of path_items so "Instancable" doesn't get wrapped
        PrimPathWidget.set_path_item_padding(3.5)

    def __menu_update(self):
        """Update the menu"""
        self._menu_layout = [
            MenuLayout.Menu(
                "Window",
                [
                    MenuLayout.SubMenu(
                        "Animation",
                        [
                            MenuLayout.Item("Timeline"),
                            MenuLayout.Item("Sequencer"),
                            MenuLayout.Item("Curve Editor"),
                            MenuLayout.Item("Retargeting"),
                            MenuLayout.Item("Animation Graph"),
                            MenuLayout.Item("Animation Graph Samples"),
                        ],
                    ),
                    MenuLayout.SubMenu(
                        "Layout",
                        [
                            MenuLayout.Item("Quick Save", remove=True),
                            MenuLayout.Item("Quick Load", remove=True),
                        ],
                    ),
                    MenuLayout.SubMenu(
                        "Browsers",
                        [
                            MenuLayout.Item("Content", source="Window/Content"),
                            MenuLayout.Item("Materials"),
                            MenuLayout.Item("Skies"),
                        ],
                    ),
                    MenuLayout.SubMenu(
                        "Rendering",
                        [
                            MenuLayout.Item("Render Settings"),
                            MenuLayout.Item("Movie Capture"),
                            MenuLayout.Item("MDL Material Graph"),
                            MenuLayout.Item("Tablet XR"),
                        ],
                    ),
                    MenuLayout.SubMenu(
                        "Utilities",
                        [
                            MenuLayout.Item("Console"),
                            MenuLayout.Item("Profiler"),
                            MenuLayout.Item("USD Paths"),
                            MenuLayout.Item("Statistics"),
                            MenuLayout.Item("Activity Progress"),
                            MenuLayout.Item("Actions"),
                            MenuLayout.Item("Asset Validator"),
                        ],
                    ),
                    MenuLayout.Sort(
                        exclude_items=["Extensions"], sort_submenus=True
                    ),
                    MenuLayout.Item("New Viewport Window", remove=True),
                ],
            ),
            MenuLayout.Menu(
                "Layout",
                [
                    MenuLayout.Item("Default", source="Reset Layout"),
                    MenuLayout.Seperator(),
                    MenuLayout.Item(
                        "UI Toggle Visibility",
                        source="Window/UI Toggle Visibility"
                    ),
                    MenuLayout.Item(
                        "Fullscreen Mode", source="Window/Fullscreen Mode"
                    ),
                    MenuLayout.Seperator(),
                    MenuLayout.Item(
                        "Save Layout", source="Window/Layout/Save Layout..."
                    ),
                    MenuLayout.Item(
                        "Load Layout", source="Window/Layout/Load Layout..."
                    ),
                    MenuLayout.Seperator(),
                    MenuLayout.Item(
                        "Quick Save", source="Window/Layout/Quick Save"
                    ),
                    MenuLayout.Item(
                        "Quick Load", source="Window/Layout/Quick Load"
                    ),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(self._menu_layout)

        self._layout_menu_items = []

        def add_layout_menu_entry(name, parameter, key):
            """Add a layout menu entry."""
            if inspect.isfunction(parameter):
                menu_dict = omni.kit.menu.utils.build_submenu_dict(
                    [
                        MenuItemDescription(name=f"Layout/{name}",
                                            onclick_fn=lambda: asyncio.ensure_future(parameter()),
                                            hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, key)),
                    ]
                )
            else:
                async def _active_layout(layout):
                    await _load_layout(layout)
                    # load layout file again to make sure layout correct
                    await _load_layout(layout)

                menu_dict = omni.kit.menu.utils.build_submenu_dict(
                    [
                        MenuItemDescription(name=f"Layout/{name}",
                                            onclick_fn=lambda: asyncio.ensure_future(_active_layout(f"{DATA_PATH}/layouts/{parameter}.json")),
                                            hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, key)),
                    ]
                )

            # add menu
            for group in menu_dict:
                omni.kit.menu.utils.add_menu_items(menu_dict[group], group)

            self._layout_menu_items.append(menu_dict)

        add_layout_menu_entry(
            "Reset Layout", "default", carb.input.KeyboardInput.KEY_1
        )

        # create Quick Load & Quick Save
        async def quick_save():
            QuickLayout.quick_save(None, None)

        async def quick_load():
            QuickLayout.quick_load(None, None)

        add_layout_menu_entry(
            "Quick Save", quick_save, carb.input.KeyboardInput.KEY_7
        )
        add_layout_menu_entry(
            "Quick Load", quick_load, carb.input.KeyboardInput.KEY_8
        )

        # open "Asset Stores" window
        ui.Workspace.show_window("Asset Stores")

    def on_shutdown(self):
        """Clean up the extension"""
        omni.kit.menu.utils.remove_layout(self._menu_layout)
        self._menu_layout = None

        for menu_dict in self._layout_menu_items:
            for group in menu_dict:
                omni.kit.menu.utils.remove_menu_items(menu_dict[group], group)

        self._layout_menu_items = None
        self._launcher_menu = None
        self._reset_menu = None
