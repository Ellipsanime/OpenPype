from typing import Any

from openpype.modules.shotgun.tray.credential_dialog import CredentialsDialog
from Qt import QtWidgets

class ShotgunTrayWrapper:
    module: Any
    credentials_dialog: CredentialsDialog

    def __init__(self, module) -> None:
        self.module = module
        self.credentials_dialog = CredentialsDialog(module)

    def show_credential_dialog(self):
        self.credentials_dialog.show()
        self.credentials_dialog.activateWindow()
        self.credentials_dialog.raise_()

    def tray_menu(self, tray_menu):
        print(type(tray_menu))
        menu = QtWidgets.QMenu("Shotgun", tray_menu)
        tray_menu.addMenu(menu)

    def validate(self):
        self.show_credential_dialog()
        return True

