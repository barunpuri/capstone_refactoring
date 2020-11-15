from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal

import sys

sys.path.append("./controller")
if __name__ == '__main__':
    sys.path.append("./../controller")
import controller

class SignUpForm(QtWidgets.QDialog):
    def __init__(self, signal, parent=None, MAIN_ICON = "./../img/Logo.png"):
        QtWidgets.QDialog.__init__(self, parent)
        self.clear()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.ui.setWindowTitle('Touch On Screen')
        self.setWindowIcon(QtGui.QIcon(MAIN_ICON))
        self.signal = signal
        self.signal.signup.connect(self.move_n_show)
        self.hide()

    def clear(self):
        self.ui = uic.loadUi("./../ui/signup.ui", self) 

    def closeEvent(self, QCloseEvent):
        self.signal.close.emit(QCloseEvent)
        self.clear()

    def keyPressEvent(self, event):
        pass

    @pyqtSlot()
    def go_login(self):
        self.signal.login.emit(self.x(), self.y())
        self.hide()

    @pyqtSlot()
    def signup_confirm(self):
        if(self.ui.id_box.text() == '' or self.ui.pw_box.text() == '' or self.ui.name_box.text() == '' or self.ui.email_box.text() == ''):
            self.ui.result.setText("id를 입력해주세요")
            return
        sock = controller.make_connection('signup')
        if(self.ui.pw_box.text() != self.ui.pw_check_box.text()):
            self.ui.result.setText("비밀번호가 다릅니다.")
            return 
        
        recvData = controller.send_signup_info(self.ui.id_box.text(), self.ui.pw_box.text(), self.ui.name_box.text(), self.ui.email_box.text())

        if(recvData == 'ok'):
            self.signal.login.emit(self.x(), self.y())
            self.hide()
            self.clear()
        else:
            self.ui.result.setText("이미 존재하는 ID 입니다.")
  
    def move_n_show(self, x=0, y=0):
        self.move(x,y)
        self.show()