import os
from typing import Any

from Qt import QtWidgets

from openpype.modules.default_modules.shotgrid.lib import credentials
from openpype.modules.default_modules.shotgrid.tray.batch_dialog import (
    BatchDialog,
)
from openpype.modules.default_modules.shotgrid.tray.credential_dialog import (
    CredentialsDialog,
)
from openpype.modules.default_modules.shotgrid.tray.manager_api import (
    ManagerApi,
)


class ShotgridTrayWrapper:
    module: Any
    credentials_dialog: CredentialsDialog
    logged_user_label: QtWidgets.QAction

    def __init__(self, module) -> None:
        self.module = module
        self.credentials_dialog = CredentialsDialog(module)
        self.credentials_dialog.login_changed.connect(self.set_login_label)
        self.batch_dialog = BatchDialog(module)
        self.logged_user_label = QtWidgets.QAction("")
        self.logged_user_label.setDisabled(True)
        self.set_login_label()

    def show_batch_dialog(self):
        # pass
        api = ManagerApi()
        manager_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    "manager/index.html")
        webview.create_window('Shotgrid Manager', url=manager_path,
                              js_api=api, min_size=(785, 500),
                              width=785, height=480)
        webview.start(gui='cef')

    def show_connect_dialog(self):
        self.show_credential_dialog()

    def show_credential_dialog(self):
        self.credentials_dialog.show()
        self.credentials_dialog.activateWindow()
        self.credentials_dialog.raise_()

    def set_login_label(self):
        login = credentials.get_local_login()
        if login:
            self.logged_user_label.setText("{}".format(login))
        else:
            self.logged_user_label.setText("No User logged in".format(login))

    def tray_menu(self, tray_menu):
        # Add login to user menu
        menu = QtWidgets.QMenu("Shotgrid", tray_menu)
        show_connect_action = QtWidgets.QAction("Connect to Shotgrid", menu)
        show_connect_action.triggered.connect(self.show_connect_dialog)
        menu.addAction(self.logged_user_label)
        menu.addSeparator()
        menu.addAction(show_connect_action)
        tray_menu.addMenu(menu)

        # Add manager to Admin menu
        for m in tray_menu.findChildren(QtWidgets.QMenu):
            if m.title() == "Admin":
                shotgrid_manager_action = QtWidgets.QAction("Shotgrid manager",
                                                            menu)
                shotgrid_manager_action.triggered.connect(
                    self.show_batch_dialog)
                m.addAction(shotgrid_manager_action)

    def validate(self) -> bool:
        login = credentials.get_local_login()

        if not login:
            self.show_credential_dialog()
        else:
            os.environ['OPENPYPE_SG_USER'] = login

        return True
