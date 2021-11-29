import sys, os, io, traceback

from PySide2 import QtCore, QtGui, QtWidgets

my_desktop = r"C:\Users\selami.boudjerda\Desktop"
sys.path.append(my_desktop)

import dispatcher2, utils, sanitycheck_manager_ui

TITLE = 'Sanity Check Manager'


def make_street_light_icon(color):
    pixmap = QtGui.QPixmap(QtCore.QSize(16, 10))
    pixmap.fill(QtCore.Qt.transparent)
    try:
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(painter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        painter.drawEllipse(pixmap.rect().adjusted(4, 2,-4, 0))
    finally:
        painter.end()
    return QtGui.QIcon(pixmap)



class SanityCheckSelectorDialog(QtWidgets.QDialog, sanitycheck_manager_ui.Ui_Dialog):

    # widget items data roles
    SANITYCHECK_MODULE = QtCore.Qt.UserRole
    IS_CHECKED = QtCore.Qt.UserRole+1

    def __init__(self, parent=None):
        super(SanityCheckSelectorDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(TITLE)

        self.listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.context_menu = QtWidgets.QMenu(self)
        self.action_check = self.context_menu.addAction('check')
        self.action_highlight = self.context_menu.addAction('highlight')
        self.action_resolve = self.context_menu.addAction('resolve')

        self.icons = {
            'standby': make_street_light_icon('#FFBB00'),
            'failed': make_street_light_icon('#FF0000'),
            'success': make_street_light_icon('#00FF00'),
        }

        path = self.sceneName()
        if path:
            print "PATH = ", path
            sanitychecks = dispatcher2.get_sanity_checks(os.path.basename(path))

            for sc in sanitychecks:
                try:
                    name = str(sc.name())
                except:
                    name = sc.__name__
                item = QtWidgets.QListWidgetItem(name)
                item.setData(self.SANITYCHECK_MODULE, sc)
                item.setData(self.IS_CHECKED, False)
                item.setIcon(self.icons['standby'])
                self.listWidget.addItem(item)

        self.listWidget.itemDoubleClicked.connect(self.runSanityCheck)
        self.listWidget.customContextMenuRequested[QtCore.QPoint].connect(self.contextMenuRequested)
        self.action_check.triggered.connect(self.checkActionTriggered)
        self.action_highlight.triggered.connect(self.highlightActionTriggered)
        self.action_resolve.triggered.connect(self.resolveActionTriggered)

    def sceneName(self):
        import maya.cmds as mc
        sn = mc.file(q=1, sn=1)
        if sn:
            return sn
        loc = mc.file(q=1, loc=1)
        if loc != "unknown":
            return loc


    def accept(self):
        for item in self.listWidget.selectedItems():
            sc = item.data(self.SANITYCHECK_MODULE)
            utils.run_sanity_check(sc)


    def runSanityCheck(self, item):
        sc = item.data(self.SANITYCHECK_MODULE)
        ok = utils.run_sanity_check(sc)
        status = 'success' if ok else 'failed'
        item.setData(self.IS_CHECKED, True)
        item.setIcon(self.icons[status])


    def checkActionTriggered(self):
        for item in self.listWidget.selectedItems():
            self.runSanityCheck(item)


    def highlightActionTriggered(self):
        for item in self.listWidget.selectedItems():
            if not item.data(self.IS_CHECKED):
                continue
            sc = item.data(self.SANITYCHECK_MODULE)
            try:
                sc.highlight()
            except AttributeError:
                sys.stdout.write('"{}" sanity check has no "highlight" function!\n'.format(item.text()))
                continue


    def resolveActionTriggered(self):
        for item in self.listWidget.selectedItems():
            if not item.data(self.IS_CHECKED):
                continue
            sc = item.data(self.SANITYCHECK_MODULE)
            try:
                sc.resolve()
            except AttributeError:
                sys.stdout.write('"{}" sanity check has no "resolve" function!\n'.format(item.text()))
                continue
            if not sc.check():
                item.setIcon(self.icons['failed'])
            else:
                item.setIcon(self.icons['success'])


    def contextMenuRequested(self, pos):
        sanity_checks = [ item.data(self.SANITYCHECK_MODULE) for item in self.listWidget.selectedItems() if item.data(self.IS_CHECKED) ]
        self.action_highlight.setEnabled(any( hasattr(sc, 'highlight') for sc in sanity_checks ))
        self.action_resolve.setEnabled(any( hasattr(sc, 'resolve') for sc in sanity_checks ))
        global_pos = self.listWidget.viewport().mapToGlobal(pos)
        self.context_menu.exec_(global_pos)


def getMayaMainWindow():
    from maya import OpenMayaUI
    from shiboken2 import wrapInstance
    from PySide2.QtWidgets import QWidget
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QWidget)

def show():
    mw = getMayaMainWindow()
    dlg = SanityCheckSelectorDialog(mw)
    dlg.show()

if __name__ == "__main__":

    show()
