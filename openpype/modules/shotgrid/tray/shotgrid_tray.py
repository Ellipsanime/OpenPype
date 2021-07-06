from typing import Any

from openpype.modules.shotgrid.tray.credential_dialog import CredentialsDialog
from Qt import QtWidgets


class ShotgridTrayWrapper:
    module: Any
    credentials_dialog: CredentialsDialog

    def __init__(self, module) -> None:
        self.module = module
        self.credentials_dialog = CredentialsDialog(module)

    def show_connect_dialog(self):
        self.show_credential_dialog()

    def show_credential_dialog(self):
        self.credentials_dialog.show()
        self.credentials_dialog.activateWindow()
        self.credentials_dialog.raise_()

    def tray_menu(self, tray_menu):
        menu = QtWidgets.QMenu("Shotgrid", tray_menu)
        show_connect_action = QtWidgets.QAction("Connect to Shotgrid", menu)
        show_connect_action.triggered.connect(self.show_connect_dialog)
        menu.addAction(show_connect_action)

        tray_menu.addMenu(menu)

    def validate(self):
        self.show_credential_dialog()
        return True
