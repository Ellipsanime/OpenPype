import sys
import os
from typing import Any

from openpype.modules.default_modules.shotgrid.tray.credential_dialog import (
    CredentialsDialog,
)
from openpype.modules.default_modules.shotgrid.tray.batch_dialog import (
    BatchDialog,
)
from openpype.modules.default_modules.shotgrid.tray.manager_api import (
    ManagerApi,
)
from openpype.modules.default_modules.shotgrid.lib import credentials, settings

from Qt import QtWidgets
import webview


class ShotgridTrayWrapper:
    module: Any
    credentials_dialog: CredentialsDialog

    def __init__(self, module) -> None:
        self.module = module
        self.credentials_dialog = CredentialsDialog(module)
        self.batch_dialog = BatchDialog(module)

    def show_batch_dialog(self):
        # pass
        api = ManagerApi()
        manager_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    "manager/index.html")
        webview.create_window('Shotgrid Manager', url=manager_path,
                              js_api=api, min_size=(790, 500))
        webview.start(gui='cef', debug=False)


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
        show_batch_action = QtWidgets.QAction("Launch Batch", menu)
        show_batch_action.triggered.connect(self.show_batch_dialog)
        menu.addAction(show_connect_action)
        menu.addAction(show_batch_action)
        tray_menu.addMenu(menu)

    def validate(self) -> bool:
        shotgrid_url = settings.get_shotgrid_url()

        if not shotgrid_url:
            self.show_credential_dialog()
            return True

        cred = credentials.get_credentials(settings.get_shotgrid_url())

        if cred.is_empty():
            self.show_credential_dialog()
        return True
