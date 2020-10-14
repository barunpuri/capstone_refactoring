from socket import *
import threading
import time
import pyautogui
import webbrowser
import sys
import platform
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from win10toast import ToastNotifier
import os
from tkinter import *
from PIL import Image, ImageTk
import json
import uuid

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


def make_popup_image(mode):
    SIZE = 250
    root = Tk()
    root.wm_attributes("-alpha", '0.6')
    root.overrideredirect(1)
    root.lift()
    root.wm_attributes("-topmost", 1)
    root.geometry("{}x{}+{}+{}".format(SIZE, SIZE, int((WIDTH-SIZE)/2), int((HEIGHT-SIZE)/2)) )

    photo = PhotoImage()
    img_files = ['img/click.png', 'img/left.png', 'img/right.png', 'img/locked.png', 'img/unlocked.png']
    photo = PhotoImage(file = img_files[mode])
        
    label = Label(root, image=photo)
    label.pack()

    root.after(1000, lambda: root.destroy())
    root.mainloop()

def point_on_screen(recvData):
    try:
        mode, x_ratio, y_ratio = recvData.split(',')
        # mode 0 = click, 1 = left, 2 = right, 3 = lock, 4 = unlock 

        point_x = WIDTH * float(x_ratio) #ratio 범위 check 
        point_y = HEIGHT * float(y_ratio)

        print("좌표 : {}, {}".format(point_x,point_y) )
        mode = int(mode)
        if(mode == 0):# enum으로 바꾸기 
            pyautogui.click(x=point_x, y=point_y)
        elif( mode == 1):
            pyautogui.press('left')
        elif( mode == 2):
            pyautogui.press('right')
        elif( mode == 3): # 
            pass 
        elif( mode == 4):
            pass

        p = threading.Thread(target = make_popup_image, args=(int(mode),), daemon=True )
        p.start()

    except: # -> except 처리 value error -> 위치 옮기기
        # recv data 찍기 # logging 
        p = threading.Thread(target = make_popup_image, args=(int(recvData),), daemon=True )
        p.start()
        pass # pass.. 삭제! 
        # 완성된 상태에서 발생할 경우가 없다면 삭제..! 

def make_connection(id): # request ...같은 이름으로 바꾸기 
    port = 8081

    clientSock = socket(AF_INET, SOCK_STREAM)
    clientSock.connect(('127.0.0.1', port))
    #clientSock.connect(('13.125.89.118', port))    
        # ip, port ->  ini 파일로...
    ##꼭 connection을 매번 연결 해야하는가?
    ## 한번 연결한거를 계속 쓰면? 
    ## client, server가 여러 socket을 갖는것은 부적절 
    ## client에서 server로 보내는것을 thread로 한다면!
        ## 그 thread가 길어진다면 괜찮은데 
        ## 그게 아니면 별로 
        

    print('접속 완료')

    if( id == 'pw' ):
        sendData = 'com'
        clientSock.send(sendData.encode('utf-8'))

        password = clientSock.recv(1024).decode('utf-8')

        #화면에 비밀번호 보여주기 
        print("pw : " + password)
        return password, clientSock # => return value의 형식을 통일
                                    # => 공통된 return값을 앞쪽으로  
    
    elif( id == 'login' or id == 'signup'):
        sendData = id
        clientSock.send(sendData.encode('utf-8'))
        
        return clientSock # 
    
def pointing_start(sock):
    # 좌표값 
    recvData = ''
    while True: # socket 에러 처리 필요 
        recvData = sock.recv(1024).decode('utf-8')
        if( recvData == 'test' ) : # test코드 삭제 
            continue
        elif( recvData == 'disconnected with other device'): 
            sock.close()
            break # 재접속 여부 확인 
        elif( recvData == 'closed' ):
            sock.close()
            break

        print('입력 :', recvData)  # '0, 0.7, 0.5'
        
        p = threading.Thread(target = point_on_screen, args=(recvData,), daemon=True )
        p.start()
    
    return recvData

def connectionStart(sock, QDialog): # thread로 만든 이유 -> 일반 함수로 해도 될거 같은데... # ui처리랑 동시에 하려고 
    #연결 성공 
    while True: # connection단계에서는 ui를 못쓰게 하는게 맞는거 같다 
        recvData = sock.recv(1024).decode('utf-8')
        if( recvData == 'Connected' ):
            QDialog.ui.status.setText('연결되었습니다')
            QDialog.ui.pw_label_2.setText('')
            print(recvData)
            break

    res = pointing_start(sock) #이거만 thread를 빼는거도 나을거 같다 

    if( res == 'disconnected with other device'):
        QDialog.ui.status.setText('연결이 종료되었습니다. \n다시 연결하려면 번호를 다시 생성해 주세요')
        QDialog.ui.pw_label_2.setText('')
    
def notify():
    if( platform.system() == 'Windows' and platform.release() == '10'):
        toaster = ToastNotifier()
        toaster.show_toast("Touch On Screen", "Program is running in System Tray~", icon_path="img/Logo.ico", duration=4, threaded=True)

class MainForm(QtWidgets.QDialog):
    def __init__(self, parent=None):
        self.closed = 0
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.ui = uic.loadUi("tos_v1.ui", self) #tos.ui
        self.setFixedSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.ui.setWindowTitle('Touch On Screen')
        self.setWindowIcon(QtGui.QIcon(MAIN_ICON))
        
    def showNormal(self):
        trayIcon.hide()
        self.show()
    
    def keyPressEvent(self, event): 
        pass
    # Did the user press the Escape key?
    #if event.key() == QtCore.Qt.Key_Escape: # QtCore.Qt.Key_Escape is a value that equates to what the operating system passes to python from the keyboard when the escape key is pressed.
        # Yes: Close the window
        #self.close()
    # No:  Do nothing.

    @pyqtSlot()
    def generate_num(self): # btn 
        #self.ui.pw_show.setText("1234")

        pw, sock = make_connection('pw')
        #화면에 pw 보여주기 gui
        self.ui.pw_label_2.setText(pw) #이름 바꾸기! 
        self.ui.status.setText('연결할 장비에 아래 비밀번호를 입력하세요.')
        
        waiting = threading.Thread(target=connectionStart, args=(sock,self))
        waiting.start()

    @pyqtSlot()
    def how_to(self): #btn
        webbrowser.open("https://github.com/kookmin-sw/capstone-2020-9")

    @pyqtSlot()
    def login(self): #btn
        login_window.move(self.x(), self.y())
        self.hide()
        login_window.show()

    def closeEvent(self, QCloseEvent):
        print("WindowCLoseEvent")
        trayIcon.show()
        if( self.closed == 0 ):
            noti = threading.Thread(target=notify)
            noti.start()
        self.closed += 1

    def restore(self, reason):
        if reason == SystemTrayIcon.DoubleClick:
            trayIcon.hide()
            # self.showNormal will restore the window even if it was
            # minimized.
            self.show()

class LoginForm(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.ui = uic.loadUi("login.ui", self) 
        self.setFixedSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.ui.setWindowTitle('Touch On Screen')
        self.setWindowIcon(QtGui.QIcon(MAIN_ICON))

    def closeEvent(self, QCloseEvent):
        main_window.closeEvent(QCloseEvent)
        self.__init__()

    def keyPressEvent(self, event):
        pass

    @pyqtSlot()
    def send_login_info(self):
        sock = make_connection('login') 
        login_info = dict() # server -> login info class 가져가 쓰기 => 공통 구조로 쓸 수 있으면 따로 python파일로 빼기  # 데이터 구조는 같고 행동이 다르면 상속 구조로 쓰는것도 방법 
        login_info["id"] = self.ui.id_box.text()
        login_info["pw"] = self.ui.pw_box.text()
        login_info["did"] = gethostname()
        login_info["mac"] = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
        sock.send(json.dumps(login_info).encode('utf-8'))
        recvData = sock.recv(1024).decode('utf-8')
        print(recvData)
        if(recvData == 'ok'): 
            main_window.move(self.x(), self.y())
            self.hide()
            main_window.ui.pushButton_3.setEnabled(False)
            main_window.ui.status.setText("연결을 기다리고 있습니다.")
            main_window.ui.pw_label_2.setText("")
            waiting = threading.Thread(target=connectionStart, args=(sock,main_window))
            waiting.start()
            main_window.show()
        else:
            self.ui.result.setText("올바르지 않은 ID, PW 입니다.")
            
    @pyqtSlot()
    def make_account(self):
        signup_window.move(self.x(), self.y())
        self.hide()
        signup_window.show()

    @pyqtSlot()
    def go_main(self):
        main_window.move(self.x(), self.y())
        self.hide()
        main_window.show()
        self.__init__()
        
class SignUpForm(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.ui = uic.loadUi("signup.ui", self) 
        self.setFixedSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.ui.setWindowTitle('Touch On Screen')
        self.setWindowIcon(QtGui.QIcon(MAIN_ICON))

    def closeEvent(self, QCloseEvent):
        main_window.closeEvent(QCloseEvent)
        self.__init__()

    def keyPressEvent(self, event):
        pass

    @pyqtSlot()
    def go_login(self):
        login_window.move(self.x(), self.y())
        self.hide()
        login_window.show()

    @pyqtSlot()
    def signup_confirm(self):
        if(self.ui.id_box.text() == '' or self.ui.pw_box.text() == '' or self.ui.name_box.text() == '' or self.ui.email_box.text() == ''):
            self.ui.result.setText("id를 입력해주세요")
            return
        sock = make_connection('signup')
        if(self.ui.pw_box.text() != self.ui.pw_check_box.text()):
            self.ui.result.setText("비밀번호가 다릅니다.")
            return 
        
        signup_info = dict() # server -> signup class 
        signup_info["id"] = self.ui.id_box.text()
        signup_info["pw"] = self.ui.pw_box.text()
        signup_info["name"] = self.ui.name_box.text()
        signup_info["email"] = self.ui.email_box.text()
        sock.send(json.dumps(signup_info).encode('utf-8'))

        recvData = sock.recv(1024).decode('utf-8')
        if(recvData == 'ok'):
            main_window.move(self.x(), self.y())
            self.hide()
            login_window.show()
            self.__init__()
        else:
            self.ui.result.setText("이미 존재하는 ID 입니다.")
            
class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        print(parent)
        self.activated.connect(main_window.restore)
        menu = QtWidgets.QMenu(parent)

        openAction = menu.addAction("Open")
        openAction.triggered.connect(parent.showNormal)

        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(app.quit)
        
        self.setContextMenu(menu)

#fixed size = 365 305        
if __name__ == '__main__':
    WIDTH, HEIGHT = pyautogui.size()  
    MAIN_ICON = "img/Logo.png"
    print('width={0}, height={1}'.format(WIDTH, HEIGHT))

    clientSock = socket
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    main_window = MainForm()
    main_window.show()
    login_window = LoginForm()
    login_window.hide()
    signup_window = SignUpForm()
    signup_window.hide()

    trayIcon = SystemTrayIcon(QtGui.QIcon(MAIN_ICON), main_window)
    trayIcon.hide()
    app.exec()
    os._exit(0)
