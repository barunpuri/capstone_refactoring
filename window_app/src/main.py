import time
import pyautogui
import sys
import os

from PyQt5 import QtWidgets
from PyQt5 import QtGui

sys.path.append("./view")
from basic import MainForm
from login import LoginForm
from signup import SignUpForm
from systray import SystemTrayIcon

sys.path.append("./controller")
import controller

# pyqt / java 초창기 ui 문제 => drag n drop 으로 하기가 불편
# 보통 학생 -> ui -> pyqt 
# MVC 패턴 
# data처리, ui제어(view), 데이터-서버 연결(control class) 로 분리 
# main.py -> 3개로 
# view class -> 문제가 많음 -> 변동사항이 많은ㅁ
# 

### *** socket 에러 처리 필요 ***
# -> 일반적으로 socket의 wrapping class를 사용 
        # ->에러를 일관적으로 처리 
# 



#fixed size = 365 305        
if __name__ == '__main__':
    WIDTH, HEIGHT = pyautogui.size()  
    MAIN_ICON = "./../img/Logo.png"
    print('width={0}, height={1}'.format(WIDTH, HEIGHT))

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    signal = controller.Signal()
    main_window = MainForm(signal = signal)
    login_window = LoginForm(signal = signal)
    signup_window = SignUpForm(signal = signal)

    app.exec()
    os._exit(0)
