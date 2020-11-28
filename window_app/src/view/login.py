from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal

import sys
import uuid

sys.path.append("./controller")
if __name__ == '__main__':
    sys.path.append("./../controller")
import controller

class LoginForm(QtWidgets.QDialog):
    def __init__(self, signal, parent=None, MAIN_ICON = "./../img/Logo.png"):
        QtWidgets.QDialog.__init__(self, parent)
        self.clear()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.ui.setWindowTitle('Touch On Screen')
        self.setWindowIcon(QtGui.QIcon(MAIN_ICON))
        self.signal = signal
        self.signal.login.connect(self.move_n_show)
        self.hide()

    def clear(self):
        self.ui = uic.loadUi("./../ui/login.ui", self)  # ui load 대신 
                                                        # id pw ..이런거 삭제 
                                                        # 

    def closeEvent(self, QCloseEvent):          # main의 close 와 연결 .... 
        self.signal.close.emit(QCloseEvent)     # 보통 ui가 
        self.clear()                            # ui 재사용 -> 갖고있는 정보를 유지해야 하는 경우
                                                # 기존의 instance 를 파괴..
                                                # -> 새 생성

    def keyPressEvent(self, event):
        pass

    @pyqtSlot()
    def send_login_info(self):
        sock = controller.make_connection('login') 
        recvData = controller.send_login_info(sock, self.ui.id_box.text(), self.ui.pw_box.text())
        print(recvData)
        if(recvData == 'ok'): 
            self.signal.basic.emit(self.x(), self.y())
            self.hide()
            self.signal.loggined.emit(sock)
        else:
            self.ui.result.setText("올바르지 않은 ID, PW 입니다.")
            
    @pyqtSlot()
    def make_account(self):
        self.signal.signup.emit(self.x(), self.y())
        self.hide()

    @pyqtSlot()
    def go_main(self):
        self.signal.basic.emit(self.x(), self.y())
        self.hide()
        self.clear()
    
    def move_n_show(self, x=0, y=0):
        print("login")
        self.move(x,y)
        self.show()