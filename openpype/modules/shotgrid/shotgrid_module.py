import os
from typing import Optional, Dict, AnyStr, Any
from openpype.modules.shotgrid.lib import credentials
import shotgun_api3

from openpype.modules import (
    PypeModule,
    ITrayModule,
    IPluginPaths,
    ILaunchHookPaths,
)
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
        shotgrid_url = shotgrid_settings.get("shotgrid_server").strip()

        self.shotgrid_url = shotgrid_url

        self.project_id = shotgrid_settings.get("project_id")

        # if self.enabled and not self.project_id:
        #     raise Exception("Project id is not set in settings.")

    def connect_with_modules(self, enabled_modules):
        pass

    def get_global_environments(self) -> Dict[AnyStr, Any]:
        return {"PROJECT_ID": self.project_id}

    def get_plugin_paths(self) -> Dict[AnyStr, Any]:
        return {
            "publish": [
                os.path.join(SHOTGRID_MODULE_DIR, "plugins", "publish")
            ]
        }

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

    def set_credentials_to_env(self, username: AnyStr, api_key: AnyStr):
        os.environ["SHOTGRID_LOGIN"] = username or ""
        os.environ["SHOTGRID_PASSWORD"] = api_key or ""

    def create_shotgrid_session(self) -> shotgun_api3.Shotgun:
        credentials_ = credentials.get_credentials()
        return shotgun_api3.Shotgun(
            base_url=self.shotgrid_url,
            login=credentials_.get("login"),
            password=credentials_.get("password"),
        )
