import os
from typing import Optional, Dict, Any
from openpype.modules.default_modules.shotgrid.lib import settings, credentials
import shotgun_api3

from openpype.modules import OpenPypeModule

from openpype_interfaces import (
    ITrayModule,
    IPluginPaths,
    ILaunchHookPaths,
)
from openpype.modules.default_modules.shotgrid.tray.shotgrid_tray import (
    ShotgridTrayWrapper,
)

SHOTGRID_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


class ShotgridModule(
    OpenPypeModule, ITrayModule, IPluginPaths, ILaunchHookPaths
):
    name: str = "shotgrid"
    enabled: bool = False
    project_id: Optional[str] = None
    tray_wrapper: ShotgridTrayWrapper

    def initialize(self, modules_settings: Dict[str, Any]):
        shotgrid_settings = modules_settings.get(self.name, dict())
        self.enabled = shotgrid_settings.get("enabled", False)
        shotgrid_url = shotgrid_settings.get("shotgrid_url").strip()

        self.shotgrid_url = shotgrid_url

        self.project_id = shotgrid_settings.get("project_id")

        # if self.enabled and not self.project_id:
        #     raise Exception("Project id is not set in settings.")

    def connect_with_modules(self, enabled_modules):
        pass

    def get_global_environments(self) -> Dict[str, Any]:
        return {"PROJECT_ID": self.project_id}

    def get_plugin_paths(self) -> Dict[str, Any]:
        return {
            "publish": [
                os.path.join(SHOTGRID_MODULE_DIR, "plugins", "publish")
            ]
        }

    def get_launch_hook_paths(self) -> str:
        return os.path.join(SHOTGRID_MODULE_DIR, "hooks")

    def tray_init(self):
        self.tray_wrapper = ShotgridTrayWrapper(self)

    def tray_start(self):
        return self.tray_wrapper.validate()

    def tray_exit(self, *args, **kwargs):
        return self.tray_wrapper

    def tray_menu(self, tray_menu):
        return self.tray_wrapper.tray_menu(tray_menu)

    def create_shotgrid_session(self) -> shotgun_api3.Shotgun:
        credentials_ = credentials.get_credentials(settings.get_shotgrid_url())
        return shotgun_api3.Shotgun(
            base_url=self.shotgrid_url,
            login=credentials_.login,
            password=credentials_.password,
        )
