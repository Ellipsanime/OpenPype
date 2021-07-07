from typing import Any
from Qt import QtCore, QtWidgets, QtGui

from openpype import style
from openpype import resources
from openpype.api import get_system_settings

import shotgun_api3
from shotgun_api3.shotgun import AuthenticationFault


class CredentialsDialog(QtWidgets.QDialog):
    SIZE_W = 450
    SIZE_H = 150

    _module: Any = None
    _is_logged: bool = False
    url_label: QtWidgets.QLabel
    login_label: QtWidgets.QLabel
    password_label: QtWidgets.QLabel
    url_input: QtWidgets.QLineEdit
    login_input: QtWidgets.QLineEdit
    password_input: QtWidgets.QLineEdit
    input_layout: QtWidgets.QFormLayout
    login_button: QtWidgets.QPushButton
    buttons_layout: QtWidgets.QHBoxLayout
    input_layout: QtWidgets.QFormLayout
    main_widget: QtWidgets.QVBoxLayout

    def __init__(self, module, parent=None):
        super(CredentialsDialog, self).__init__(parent)

        self._module = module
        self._is_logged = False

        self.setWindowTitle("OpenPype - Shotgrid Login")

        icon = QtGui.QIcon(resources.pype_icon_filepath())
        self.setWindowIcon(icon)

        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowMinimizeButtonHint
        )
        self.setMinimumSize(QtCore.QSize(self.SIZE_W, self.SIZE_H))
        self.setMaximumSize(QtCore.QSize(self.SIZE_W + 100, self.SIZE_H + 100))
        self.setStyleSheet(style.load_stylesheet())

        self.ui_init()
        self.fill_ftrack_url()

    def ui_init(self):
        self.url_label = QtWidgets.QLabel("Shotgrid URL:")
        self.login_label = QtWidgets.QLabel("Login:")
        self.password_label = QtWidgets.QLabel("Password:")

        self.url_input = QtWidgets.QLineEdit()
        self.url_input.setReadOnly(True)

        self.login_input = QtWidgets.QLineEdit()
        self.login_input.setPlaceholderText("login")

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.error_label = QtWidgets.QLabel("")
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        self.input_layout = QtWidgets.QFormLayout()
        self.input_layout.setContentsMargins(10, 15, 10, 5)

        self.input_layout.addRow(self.url_label, self.url_input)
        self.input_layout.addRow(self.login_label, self.login_input)
        self.input_layout.addRow(self.password_label, self.password_input)
        self.input_layout.addRow(self.error_label)

        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setToolTip("Log in shotgrid instance")
        self.login_button.clicked.connect(self._on_shotgrid_login_clicked)

        self.logout_button = QtWidgets.QPushButton("Logout")
        self.logout_button.setToolTip("Log out shotgrid instance")
        self.logout_button.clicked.connect(self._on_shotgrid_logout_clicked)

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.addWidget(self.login_button)

        self.main_widget = QtWidgets.QVBoxLayout(self)
        self.main_widget.addLayout(self.input_layout)
        self.main_widget.addLayout(self.buttons_layout)
        self.setLayout(self.main_widget)

    def show(self, *args, **kwargs):
        super(CredentialsDialog, self).show(*args, **kwargs)
        self.fill_ftrack_url()

    def fill_ftrack_url(self):
        shotgrid_settings = (
            get_system_settings().get("modules", {}).get("shotgrid", {})
        )

        url = shotgrid_settings.get("shotgrid_server")

        if url:
            self.url_input.setText(url)
            enabled = True
        else:
            self.url_input.setText("Ask your admin to add the shotgrid url")
            self.login_button.hide()
            enabled = False

        self.login_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)

    def _on_shotgrid_login_clicked(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        missing = []

        if login == "":
            missing.append("login")
            self._invalid_input(self.login_input)

        if password == "":
            missing.append("password")
            self._invalid_input(self.password_input)

        if len(missing) > 0:
            self.set_error("You didn't enter {}".format(" and ".join(missing)))
            return

        if not self.login_with_credentials(login, password):
            self._invalid_input(self.user_input)
            self._invalid_input(self.api_input)
            self.set_error(
                "We're unable to sign in to Ftrack with these credentials"
            )

        try:
            sg = shotgun_api3.Shotgun(
                self.url_input.text(), login=login, password=password
            )

            sg.preferences_read()
            self._on_login()

        except AuthenticationFault as err:
            raise AuthenticationFault(err)

        except Exception as err:
            print(err)

    def _on_shotgrid_logout_clicked(self):
        pass

    def set_error(self, msg):
        self.error_label.setText(msg)
        self.error_label.show()

    def _on_login(self):
        print(
            f"You are logged into shotgrid with user {self.login_input.text()}"
        )
        self._is_logged = True
        self._close_widget()

    def _close_widget(self):
        self.hide()

    def _valid_input(self, input_widget):
        input_widget.setStyleSheet("")

    def _invalid_input(self, input_widget):
        input_widget.setStyleSheet("border: 1px solid red;")
