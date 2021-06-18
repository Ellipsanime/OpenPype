from typing import Any

from Qt import QtCore, QtWidgets

from openpype import style


class CredentialsDialog(QtWidgets.QDialog):
    SIZE_W = 300
    SIZE_H = 230

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
        self.setWindowTitle("OpenPype - Shotgun Login")

        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint
        )
        self.setMinimumSize(QtCore.QSize(self.SIZE_W, self.SIZE_H))
        self.setMaximumSize(QtCore.QSize(self.SIZE_W + 100, self.SIZE_H + 100))
        self.setStyleSheet(style.load_stylesheet())

        self.ui_init()

    def ui_init(self):
        self.url_label = QtWidgets.QLabel("Shotgun URL:")
        self.login_label = QtWidgets.QLabel("Login:")
        self.password_label = QtWidgets.QLabel("Password:")
        # self.url_input = QtWidgets.QLabel()
        # self.url_input.setTextInteractionFlags(
        #     QtCore.Qt.TextBrowserInteraction
        # )
        # self.url_input.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))

        self.url_input = QtWidgets.QLineEdit()
        self.url_input.setPlaceholderText("shotgun url")

        self.login_input = QtWidgets.QLineEdit()
        self.login_input.setPlaceholderText("login")

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("password")

        self.input_layout = QtWidgets.QFormLayout()
        self.input_layout.setContentsMargins(10, 15, 10, 5)

        self.input_layout.addRow(self.url_label, self.url_input)
        self.input_layout.addRow(self.login_label, self.login_input)
        self.input_layout.addRow(self.password_label, self.password_input)

        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setToolTip("Login into shotgun instance")
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.addWidget(self.login_button)

        self.main_widget = QtWidgets.QVBoxLayout(self)
        self.main_widget.addLayout(self.input_layout)
        self.main_widget.addLayout(self.buttons_layout)
        self.setLayout(self.main_widget)
