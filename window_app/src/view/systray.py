from win10toast import ToastNotifier
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
import sys

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, signal, icon = "./../img/Logo.png", parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        print(parent)
        self.activated.connect(self.restore)
        menu = QtWidgets.QMenu(parent)
        self.signal = signal
        self.signal.tray.connect(self.tray)

        openAction = menu.addAction("Open")
        openAction.triggered.connect(parent.showNormal)

        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(sys.exit)
        # app.quit()
        
        self.setContextMenu(menu)

        self.hide()

    def restore(self, reason):
        if reason == SystemTrayIcon.DoubleClick:
            self.hide()
            self.signal.restore.emit()

    def tray(self):
        self.show()