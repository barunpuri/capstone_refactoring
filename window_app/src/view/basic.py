import webbrowser
import sys
import os
import threading
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from systray import SystemTrayIcon

sys.path.append("./controller")
if __name__ == '__main__':
    sys.path.append("./../controller")
import controller


class MainForm(QtWidgets.QDialog):
    def __init__(self, signal, parent=None, MAIN_ICON = "./../img/Logo.png"):
        self.closed = 0
        QtWidgets.QDialog.__init__(self, parent)
        self.clear()
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setFixedSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.ui.setWindowTitle('Touch On Screen')
        self.trayIcon = SystemTrayIcon(signal, QtGui.QIcon(MAIN_ICON), self)
        self.setWindowIcon(QtGui.QIcon(MAIN_ICON))
        self.signal = signal
        self.signal.restore.connect(self.restore)
        self.signal.close.connect(self.closeEvent)
        self.signal.basic.connect(self.move_n_show)
        self.signal.loggined.connect(self.loggined)
        self.show()
        # self.ui.pw_label.setText('1234') 

    def clear(self):
        self.ui = uic.loadUi("./../ui/basic.ui", self) #tos.ui
        
    def showNormal(self):
        # trayIcon.hide()
        self.show()
    
    def keyPressEvent(self, event):     # 테스트 해보고 필요 없으면 지워도 될거
        pass                            # pass : 코드의 틀을 잡을때 error 가 없도록
                                        #       고려해봤을때 뭐 없을때 
                                        # return과 pass의 느낌이 다름 
                                        # 의미상으로는 return 
                                        # return 이 더 명확 한 것 같음
                                        # keyPress Event를 막은 이유 설명 필요 ##주석으로 

    # Did the user press the Escape key?
    #if event.key() == QtCore.Qt.Key_Escape: # QtCore.Qt.Key_Escape is a value that equates to what the operating system passes to python from the keyboard when the escape key is pressed.
        # Yes: Close the window
        #self.close()
    # No:  Do nothing.

    @pyqtSlot()
    def generate_num(self): # btn 
        sock, pw = controller.make_connection('pw') # 문자열을 쓰는것을 자제해서 미리 선언해두고 사용 필요 
        #화면에 pw 보여주기 gui
        self.ui.pw_label.setText(pw) 
        self.ui.status_label.setText('연결할 장비에 아래 비밀번호를 입력하세요.')
        
        connecting = threading.Thread(target=self.wait_mobile, args=(sock))
        connecting.start()

    def wait_mobile(self, sock):
        recvData = controller.connectionStart(sock)
        if( recvData == 'Connected'):       # text 만 달라 -> if 문 안에서 내용만 처리 -> 3항 연산자 처리 가능 
            self.ui.status_label.setText('연결되었습니다')
            self.ui.pw_label.setText('')
        else:
            self.ui.status_label.setText('ERROR')
            self.ui.pw_label.setText('')

        controller.handling_start(sock)


    @pyqtSlot()
    def how_to(self): #btn
        webbrowser.open("https://github.com/kookmin-sw/capstone-2020-9")
    

    @pyqtSlot()
    def login(self): #btn
        self.hide()     # 숨기는 것을 가장 마지막에 
        self.signal.login.emit(self.x(), self.y()) # 
        # login_window.move(self.x(), self.y())
        # login_window.show()

    def closeEvent(self, QCloseEvent): ## 지금은 이게 close event -> hide처럼 처리지만 
        print("WindowCLoseEvent")       # 나중에 누가 이해할거냐.....
        self.signal.tray.emit()
        if( self.closed == 0 ):         # 최초 닫기에만 noti => true, false
            controller.notify()         # notied = false -> true면 안함 
                                        # flag 변수 별로 안 좋아함..
                                        # 일반적으로 conf 파일에 알람을 어떻게 처리할지 저장되어 있음
            # noti = threading.Thread(target=notify)
            # noti.start()
        self.closed += 1

    def restore(self):
        self.show()

    def move_n_show(self, x=0, y=0):
        self.move(x,y)
        self.show()

    def loggined(self, sock):
        self.ui.login_btn.setEnabled(False)
        self.ui.status_label.setText("연결을 기다리고 있습니다.")
        self.ui.pw_label.setText("")
        
        connecting = threading.Thread(target=self.wait_mobile, args=(sock))
        connecting.start()
        

if __name__ == '__main__':
    import pyautogui
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    WIDTH, HEIGHT = pyautogui.size()  
    MAIN_ICON = "./../img/Logo.png"
    print('width={0}, height={1}'.format(WIDTH, HEIGHT))
    main_window = MainForm()
    main_window.show()
    app.exec()
    os._exit(0)

    