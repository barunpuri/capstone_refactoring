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
import basic_controller as controller

from configparser import ConfigParser

parser = ConfigParser()
parser.read('config.ini')

class MainForm(QtWidgets.QDialog):
    def __init__(self, signal, parent=None, MAIN_ICON = "./../img/Logo.png"):
        self.hasNotied = False
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("./../ui/basic.ui", self)
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
        self.signal.disconnected.connect(self.disconnected)
        self.show()
        # self.ui.pw_label.setText('1234') 

    def clear(self):
        self.ui.pw_label.setText("")
        self.ui.status_label.setText("")
        
    def showNormal(self):
        # trayIcon.hide()
        self.show()
    
    def keyPressEvent(self, event):   
        # block key press event "esc" 
        # if not exist -> hide window
        return                          
        # pass : 코드의 틀을 잡을때 error 가 없도록
        #       고려해봤을때 뭐 없을때 
        # return과 pass의 느낌이 다름 
        # 의미상으로는 return 
        # return 이 더 명확 한 것 같음
                                        
    # Did the user press the Escape key?
    #if event.key() == QtCore.Qt.Key_Escape: # QtCore.Qt.Key_Escape is a value that equates to what the operating system passes to python from the keyboard when the escape key is pressed.
        # Yes: Close the window
        #self.close()
    # No:  Do nothing.

    @pyqtSlot()
    def generate_num(self): # btn 
        sock, pw = controller.make_connection()
        #화면에 pw 보여주기 gui
        self.ui.pw_label.setText(pw) 
        self.ui.status_label.setText('연결할 장비에 아래 비밀번호를 입력하세요.')
        
        connecting = threading.Thread(target=self.wait_mobile, args=(sock))
        connecting.start()

    def wait_mobile(self, sock):
        recvData = controller.connectionStart(sock)
        result_text = ''
        if( recvData == 'Connected'):  
            result_text = '연결되었습니다'
        else:
            result_text = 'ERROR'
            
        self.ui.status_label.setText(result_text)
        self.ui.pw_label.setText('')
        controller.handling_start(sock, self.signal)


    @pyqtSlot()
    def how_to(self): #btn
        webbrowser.open("https://github.com/kookmin-sw/capstone-2020-9")
    

    @pyqtSlot()
    def login(self): #btn
        self.signal.login.emit(self.x(), self.y()) 
        self.hide()

    # 닫기 버튼 -> closeEvent
    def closeEvent(self, QCloseEvent): 
        print("WindowCLoseEvent")      
        self.signal.tray.emit()
        if( not self.hasNotied ):       
            controller.notify()          
            # 일반적으로 conf 파일에 알람을 어떻게 처리할지 저장되어 있음
        self.hasNotied = True

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
    
    def disconnected(self):
        self.ui.status_label.setText('연결이 종료되었습니다. \n다시 연결하려면 번호를 다시 생성해 주세요')
        self.ui.pw_label.setText('')
        

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

    