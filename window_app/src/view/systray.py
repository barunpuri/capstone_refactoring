from win10toast import ToastNotifier
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
import sys

from configparser import ConfigParser

parser = ConfigParser()
parser.read('config.ini')

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, signal, icon = "./../img/Logo.png", parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        print(parent)
        self.parent = parent
        self.activated.connect(self.actionCheck)
        menu = QtWidgets.QMenu(parent)          
        self.signal = signal                    
        self.signal.tray.connect(self.tray)     

        openAction = menu.addAction("Open")
        openAction.triggered.connect(self.restore)

        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(sys.exit)
        # app.quit()
        
        self.setContextMenu(menu)

        self.hide()

    def actionCheck(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.restore()

    def restore(self):
        self.hide()             
        self.parent.showNormal()

    def tray(self):
        self.show()