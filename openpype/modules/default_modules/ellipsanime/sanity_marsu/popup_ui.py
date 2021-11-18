#-*- coding: utf-8 -*-

__author__ = "Boudjerda Selami"
__maintainer__ = "Boudjerda Selami"
__email__ = "selami.boudjerda@ellipsanime.net"

"""
"""

import os
from PySide2.QtCore import QFile
import PySide2.QtWidgets as QtWidgets
from PySide2.QtUiTools import QUiLoader

###############################################################################
# TEMP Local path import in order to be able to work from local repository TEMP
import sys
j_path = r"C:\Users\selami.boudjerda\git\smurfs\j_smurfs\python\j_smurfs"
if not j_path in sys.path:
    print "adding"
    sys.path.append(j_path)

import sanity.dispatcher as dispatcher
reload(dispatcher)

###############################################################################

class SanityCheckerUI(QtWidgets.QWidget):

    def __init__(self, template_path, file_name=""):
        """ Popup window displayed in maya to inform the operators if something
        has been caught by the sanity.dispatcher.py module. This information is
        sent as a dict. WIP
        Args:
            file_name (string): Name of the file to check.
        Returns:
            None
        """

        super(SanityCheckerUI, self).__init__()

        loader = QUiLoader()
        ui_instance = QFile(template_path)
        self.main_window = loader.load(ui_instance)

        # Unleash the kr... the dispatcher :'
        self.steps = dispatcher.get_step_from_filename(file_name)

        # Create information windows for each step
        for step, checker in self.steps.iteritems():
            if checker == []:
                continue
            self.create_information_widget(step, checker)

        # Activate click event to launch any needed method
        self.main_window.ok_pushButton.clicked.connect(self.close_window_btn)

        # We don't need to display the UI if it doesn't contain data to display
        if self.main_window.verticalLayout_list.count() > 1:
            self.main_window.show()
        else:
            self.__del__("Everything seems to be ok")

    ###########################################################################

    def create_information_widget(self, step, checker):

        # Create a layout and title it with the step's name
        self.widget_label = QtWidgets.QLabel(step)
        self.widget_label.setObjectName("{}_label".format(step))
        self.main_window.verticalLayout_list.addWidget(self.widget_label)

        # Create an information window
        self.main_window.step_wigdet = QtWidgets.QListWidget()
        self.main_window.verticalLayout_list.addWidget(self.main_window.step_wigdet)

        # Populate the new window with the checkers reports
        for messages in checker:
            for message in messages:
                self.main_window.step_wigdet.addItem(str(message))

    ###########################################################################

    def close_window_btn(self):
        self.main_window.close()
        self.__del__("oki")

    ###########################################################################

    def __del__(self, *args):
        print ""
        print "#"*80
        print args

###############################################################################

if __name__ == "__main__":
    template_path = (
        r"C:\Users\selami.boudjerda\git\smurfs\j_smurfs\python" \
        r"\j_smurfs\sanity\ui_template\sanity_checker_ui_template.ui")

    # THIS PART OF THE SCRIPT IS ALREADY PROCESSED IN PAUL'S WORK

    # Get the scene path
    filepath = cmds.file(query=True, sceneName=True)
    # Get the file name
    filename = os.path.basename(filepath)
    # Get the file
    raw_name, _ = os.path.splitext(filename)

    switcher_ui = SanityCheckerUI(template_path, raw_name)
