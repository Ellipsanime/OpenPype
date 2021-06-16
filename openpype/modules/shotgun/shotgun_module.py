from typing import Optional, Dict, AnyStr, Any
from Qt import QtWidgets
from openpype.modules import PypeModule, ITrayModule


class ShotgunModule(PypeModule, ITrayModule):
    name: str = "shotgun"
    enabled: bool = False
    project_id: Optional[str] = None

    def initialize(self, modules_settings: Dict[AnyStr, Any]):
        shotgun_settings = modules_settings.get(self.name, dict())
        self.enabled = shotgun_settings.get("enabled", False)
        self.project_id = shotgun_settings.get("project_id")

        # if self.enabled and not self.project_id:
        #     raise Exception("Project id is not set in settings.")

    def connect_with_modules(self, enabled_modules):
        pass

    def get_global_environments(self):
        return {"PROJECT_ID": self.project_id}

    def tray_init(self):
        pass

    def tray_start(self):
        pass

    def tray_exit(self, *args, **kwargs):
        pass

    def tray_menu(self, tray_menu):
        print(type(tray_menu))
        menu = QtWidgets.QMenu("Shotgun", tray_menu)
        tray_menu.addMenu(menu)
