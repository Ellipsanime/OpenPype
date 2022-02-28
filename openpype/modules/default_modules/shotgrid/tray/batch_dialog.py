from typing import Dict, Any, Optional
from Qt import QtCore, QtWidgets, QtGui

from openpype import style
from openpype.modules.default_modules.shotgrid.lib import settings, server
from openpype.api import Logger, resources


log = Logger().get_logger("ShotgridModule")


class BatchDialog(QtWidgets.QDialog):
    SIZE_W = 450
    SIZE_H = 200

    _module: Any = None
    project_settings: Optional[Dict[str, Any]] = None

    project_label: QtWidgets.QLabel
    project_dropdown: QtWidgets.QComboBox
    override: QtWidgets.QCheckBox

    shotgrid_url: QtWidgets.QLabel
    shotgrid_script_name: QtWidgets.QLabel
    shotgrid_script_key: QtWidgets.QLabel
    shotgrid_project_id: QtWidgets.QLabel
    error_label: QtWidgets.QLabel
    success_label: QtWidgets.QLabel

    input_layout: QtWidgets.QFormLayout
    info_layout: QtWidgets.QFormLayout
    batch_button: QtWidgets.QPushButton
    buttons_layout: QtWidgets.QHBoxLayout
    main_widget: QtWidgets.QVBoxLayout

    def __init__(self, module, parent=None):
        super(BatchDialog, self).__init__(parent)

        self._module = module

        self.setWindowTitle("OpenPype - Shotgrid Batch")

        icon = QtGui.QIcon(resources.get_resource("app_icons/shotgrid.png"))
        self.setWindowIcon(icon)

        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.WindowMinimizeButtonHint
        )
        self.setMinimumSize(QtCore.QSize(self.SIZE_W, self.SIZE_H))
        self.setMaximumSize(QtCore.QSize(self.SIZE_W + 100, self.SIZE_H + 100))
        self.setStyleSheet(style.load_stylesheet())

        self.ui_init()

    def ui_init(self):
        self.project_label = QtWidgets.QLabel("Select OpenPype project:")
        self.project_dropdown = QtWidgets.QComboBox()
        self.project_dropdown.currentIndexChanged.connect(
            self._on_project_selection_changed
        )
        self.override = QtWidgets.QCheckBox(
            "Override Openpype existing project"
        )

        self.shotgrid_url = QtWidgets.QLabel("")
        self.shotgrid_script_name = QtWidgets.QLabel("")
        self.shotgrid_script_key = QtWidgets.QLabel("")
        self.shotgrid_project_id = QtWidgets.QLabel("")

        self.error_label = QtWidgets.QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        self.success_label = QtWidgets.QLabel("")
        self.success_label.setStyleSheet("color: green;")
        self.success_label.setWordWrap(True)
        self.success_label.hide()

        self.input_layout = QtWidgets.QFormLayout()
        self.input_layout.setContentsMargins(10, 15, 10, 5)

        self.input_layout.addRow(self.project_label, self.project_dropdown)
        self.input_layout.addRow(self.override)
        self.input_layout.addRow(self.error_label)
        self.input_layout.addRow(self.success_label)

        self.info_layout = QtWidgets.QFormLayout()
        self.info_layout.setContentsMargins(10, 15, 10, 5)

        self.info_layout.addRow(
            QtWidgets.QLabel("Project ID:"), self.shotgrid_project_id
        )
        self.info_layout.addRow(
            QtWidgets.QLabel("Server URL:"), self.shotgrid_url
        )
        self.info_layout.addRow(
            QtWidgets.QLabel("Script Name:"),
            self.shotgrid_script_name,
        )
        self.info_layout.addRow(
            QtWidgets.QLabel("Script Key:"), self.shotgrid_script_key
        )

        self.batch_button = QtWidgets.QPushButton("Batch")
        self.batch_button.setToolTip("Launch Batch")
        self.batch_button.setEnabled(False)
        self.batch_button.clicked.connect(self._on_shotgrid_batch_clicked)

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.batch_button)

        self.main_widget = QtWidgets.QVBoxLayout(self)
        self.main_widget.addLayout(self.input_layout)
        self.main_widget.addLayout(self.info_layout)
        self.main_widget.addLayout(self.buttons_layout)
        self.setLayout(self.main_widget)

    def show(self, *args, **kwargs):
        self.project_dropdown.clear()
        self._fill_project_dropdown()
        super(BatchDialog, self).show(*args, **kwargs)

    def _fill_project_dropdown(self):
        avalon_projects = settings.get_project_list()
        for project in avalon_projects:
            self.project_dropdown.addItem(project)

    def _on_shotgrid_batch_clicked(self):
        project = self.project_dropdown.currentText()
        if project and self.project_settings:
            res = server.send_batch_request(
                project, self.project_settings, self.override.isChecked()
            )

            if res != 200:
                msg = "Error sending batch request"
                self.set_error(msg)
                log.error(f"{msg} for project {project}")
            else:
                msg = "Batch sent"
                self.set_success(msg)
                log.info(f"{msg} for project {project}")

    def _on_project_selection_changed(self):
        self.clear_messages()

        project = self.project_dropdown.currentText()

        if not project:
            return

        project_settings = settings.get_shotgrid_project_settings(project)

        auth_settings = project_settings.get("auth", {})
        self.shotgrid_project_id.setText(
            str(project_settings.get("shotgrid_project_id"))
        )
        self.shotgrid_url.setText(auth_settings.get("project_shotgrid_url"))
        self.shotgrid_script_name.setText(
            auth_settings.get("project_shotgrid_script_name")
        )
        self.shotgrid_script_key.setText(
            auth_settings.get("project_shotgrid_script_key")
        )

        if (
            self._check_selected_project_settings(project, project_settings)
            and self._check_server_status()
        ):
            self.project_settings = project_settings
            self.batch_button.setEnabled(True)
        else:
            self.project_settings = None
            self.batch_button.setEnabled(False)

    def set_error(self, msg: str):
        self.clear_messages()
        self.error_label.setText(msg)
        self.error_label.show()

    def set_success(self, msg: str):
        self.clear_messages()
        self.success_label.setText(msg)
        self.success_label.show()

    def clear_error(self):
        self.error_label.setText("")
        self.error_label.hide()

    def clear_success(self):
        self.success_label.setText("")
        self.success_label.hide()

    def clear_messages(self):
        self.clear_error()
        self.clear_success()

    def _close_widget(self):
        self.hide()

    def _check_selected_project_settings(
        self, project: str, settings: Dict[str, Any]
    ):
        if not server.check_batch_settings(project, settings):
            self.set_error("Can't access shotgrid project with those settings")
            return False
        return True

    def _check_server_status(self):
        if server.poll_server() != 200:
            self.set_error("Can't access module server, contact your admin")
            return False
        return True

    def _valid_input(self, input_widget: QtWidgets.QLineEdit):
        input_widget.setStyleSheet("")

    def _invalid_input(self, input_widget: QtWidgets.QLineEdit):
        input_widget.setStyleSheet("border: 1px solid red;")
