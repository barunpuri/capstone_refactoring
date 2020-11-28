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
        self.activated.connect(self.restore) # parent .show normal로 처리가능하지 않을까..?
        menu = QtWidgets.QMenu(parent)              # 같은거 같지만 다른 로직으로 처리 
        self.signal = signal                        # =>다른 사람이 봤을때 뭔가 있을거 같아서 수정 불가 
        self.signal.tray.connect(self.tray)         # 동일하게 처리 필요 

        openAction = menu.addAction("Open")
        openAction.triggered.connect(parent.showNormal)

        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(sys.exit)
        # app.quit()
        
        self.setContextMenu(menu)

        self.hide()

    def restore(self, reason):
        if reason == SystemTrayIcon.DoubleClick: # 이게 안되는건가 
            self.hide()                            # 다른
            self.signal.restore.emit()

    def tray(self):
        self.show()