import os
from typing import Optional, Dict, AnyStr, Any

from openpype.modules import PypeModule, ITrayModule, IPluginPaths, ILaunchHookPaths
from openpype.modules.shotgrid.tray.shotgrid_tray import ShotgridTrayWrapper

SHOTGRID_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


class ShotgridModule(PypeModule, ITrayModule, IPluginPaths, ILaunchHookPaths):
    name: str = "shotgrid"
    enabled: bool = False
    project_id: Optional[str] = None
    tray_wrapper: ShotgridTrayWrapper

    def initialize(self, modules_settings: Dict[AnyStr, Any]):
        shotgrid_settings = modules_settings.get(self.name, dict())
        self.enabled = shotgrid_settings.get("enabled", False)
        self.project_id = shotgrid_settings.get("project_id")

        # if self.enabled and not self.project_id:
        #     raise Exception("Project id is not set in settings.")

    def connect_with_modules(self, enabled_modules):
        pass

    def get_global_environments(self) -> Dict[AnyStr, Any]:
        return {"PROJECT_ID": self.project_id}

    def get_plugin_paths(self) -> Dict[AnyStr, Any]:
        return {"publish": [os.path.join(SHOTGRID_MODULE_DIR, "plugins", "publish")]}

    def get_launch_hook_paths(self) -> AnyStr:
        return os.path.join(SHOTGRID_MODULE_DIR, "hooks")

    def tray_init(self):
        self.tray_wrapper = ShotgridTrayWrapper(self)

    def tray_start(self):
        return self.tray_wrapper.validate()

    def tray_exit(self, *args, **kwargs):
        return self.tray_wrapper

    def tray_menu(self, tray_menu):
        return self.tray_wrapper.tray_menu(tray_menu)
