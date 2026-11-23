import omni.ui as ui
from omni.ui import scene as sc
from omni.kit.viewport.window import ViewportWindow
from .manipulator import StartMenuManipulator
from .menu_info_model import MenuInfoModel

class StartWindow:
    def __init__(self, viewport: ViewportWindow, ext_id: str):
        self._vp = viewport
        self._ext_id = ext_id
        self._scene_view = None
        self._build()

    def _build(self):
        with self._vp.get_frame(self._ext_id):
            self._scene_view = sc.SceneView()
            with self._scene_view.scene:
                StartMenuManipulator(model=MenuInfoModel())

        self._vp.viewport_api.add_scene_view(self._scene_view)

    def destroy(self):
        if self._scene_view:
            self._scene_view.destroy()

            if self._vp:
                self._vp.viewport_api.remove_scene_view(self._scene_view)

        self._scene_view = None
        self._vp = None
