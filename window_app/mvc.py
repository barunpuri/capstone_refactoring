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
from PyQt5.QtCore import pyqtSlot, pyqtSignal
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

'''
사용자의 요구사항의 변동이 많을때
ui로직을 분리하면
쓰면 좋을때
    ui를 건드리고 controller를 안건드려도 될수 있음
    test를 하고싶을떄 
        -> uitest , control test
    
쓰면 안될때 
    model이 안정화가 안되어있을때 

controller도 기능별로 하나
model별로 하나
view별로 하나 
=> 파일 분리 

사용자와 interaction ->view로
ui에서 controller생성해서 사용 
controller를 분리해서 하는것도 좋을것 같다

src / 
    -window
    -model
    -view 
'''



class UserInfo:
    def __init__(self):
        self.id = None
        self.pw = None
    
    def toJson(self):
        return '{"id":"%s", "pw":"%s"}' %(self.id, self.pw)


class LoginInfo(UserInfo):
    def __init__(self):
        super().__init__()
        self.did = None
        self.mac = None

    def toJson(self):
        return '{"id":"%s", "pw":"%s", "did":"%s", "mac":"%s"}' %(self.id, self.pw, self.did, self.mac)

class SignupInfo(UserInfo):
    def __init__(self):
        super().__init__()
        self.name = None
        self.email = None

    def toJson(self):
        return '{"id":"%s", "pw":"%s", "name":"%s", "email":"%s"}' %(self.id, self.pw, self.name, self.email)

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

class Mode(enum.Enum):
    CLICK = '0'
    LEFT = '1'
    RIGHT = '2'
    LOCK = '3'
    UNLOCK = '4'

def point_on_screen(recvData):
    try:
        mode, x_ratio, y_ratio = recvData.split(',')

        point_x = WIDTH * float(x_ratio) #ratio 범위 check 
        point_y = HEIGHT * float(y_ratio)

        print("좌표 : {}, {}".format(point_x,point_y) )
        if(mode == Mode.CLICK.value):
            pyautogui.click(x=point_x, y=point_y)
        elif(mode == Mode.LEFT.value):
            pyautogui.press('left')
        elif(mode == Mode.RIGHT.value):
            pyautogui.press('right')
        elif(mode == Mode.LOCK.value): 
            pass 
        elif(mode == Mode.UNLOCK.value):
            pass

        p = threading.Thread(target = make_popup_image, args=(int(mode),), daemon=True )
        p.start()

    except ValueError as m:
        print(recvData)
        print(m)

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
            QDialog.ui.status_label.setText('연결되었습니다')
            QDialog.ui.pw_label.setText('')
            print(recvData)
            break

    res = pointing_start(sock) #이거만 thread를 빼는거도 나을거 같다 

    if( res == 'disconnected with other device'):
        QDialog.ui.status_label.setText('연결이 종료되었습니다. \n다시 연결하려면 번호를 다시 생성해 주세요')
        QDialog.ui.pw_label.setText('')
    
def notify():
    if( platform.system() == 'Windows' and platform.release() == '10'):
        toaster = ToastNotifier()
        toaster.show_toast("Touch On Screen", "Program is running in System Tray~", icon_path="img/Logo.ico", duration=4, threaded=True)

class MainForm(QtWidgets.QDialog):
    gen_pw = pyqtSignal()
    how_to_clicked = pyqtSignal()
    login_clicked = pyqtSignal()
    main_closed = pyqtSignal()
    show_normal = pyqtSignal()
    restore_event = pyqtSignal(QtWidgets.QSystemTrayIcon.ActivationReason)

    def __init__(self, parent=None):
        self.closed = 0
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.ui = uic.loadUi("basic.ui", self) #tos.ui
        self.setFixedSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.ui.setWindowTitle('Touch On Screen')
        self.setWindowIcon(QtGui.QIcon(MAIN_ICON))
        
    def showNormal(self):
        self.show_normal.emit()
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
        self.gen_pw.emit()

    @pyqtSlot()
    def how_to(self): #btn
        self.how_to_clicked.emit()
       

    @pyqtSlot()
    def login(self): #btn
        self.login_clicked.emit()

    def closeEvent(self, QCloseEvent):
        self.main_closed.emit()
        

    def restore(self, reason):
        self.restore_event.emit(reason)
        
    
    def show_pw(self, pw):
        self.ui.pw_label.setText(pw) #이름 바꾸기! 
        self.ui.status_label.setText('연결할 장비에 아래 비밀번호를 입력하세요.')

class LoginForm(QtWidgets.QDialog):
    login_closed = pyqtSignal()
    login = pyqtSignal()
    make_account_clicked = pyqtSignal()
    go_main_clicked = pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.ui = uic.loadUi("login.ui", self) 
        self.setFixedSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.ui.setWindowTitle('Touch On Screen')
        self.setWindowIcon(QtGui.QIcon(MAIN_ICON))

    def closeEvent(self, QCloseEvent):
        self.login_closed.emit()

    def keyPressEvent(self, event):
        pass

    @pyqtSlot()
    def send_login_info(self):
        self.login.emit()        

    def get_login_info(self):
        login_info = LoginInfo()
        login_info.id =self.ui.id_box.text()
        login_info.pw = self.ui.pw_box.text()
        login_info.did = gethostname()
        login_info.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
        return login_info

    @pyqtSlot()
    def make_account(self):
        self.make_account_clicked.emit()
        

    @pyqtSlot()
    def go_main(self):
        self.go_main_clicked.emit()
        self.__init__()
        
class SignUpForm(QtWidgets.QDialog):
    signup_closed = pyqtSignal()
    go_login_clicked = pyqtSignal()
    signup = pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.ui = uic.loadUi("signup.ui", self) 
        self.setFixedSize(self.frameGeometry().width(), self.frameGeometry().height())
        self.ui.setWindowTitle('Touch On Screen')
        self.setWindowIcon(QtGui.QIcon(MAIN_ICON))

    def closeEvent(self, QCloseEvent):
        self.signup_closed.emit()

    def keyPressEvent(self, event):
        pass

    @pyqtSlot()
    def go_login(self):
        self.go_login_clicked.emit()

    @pyqtSlot()
    def signup_confirm(self):
        if(self.ui.id_box.text() == '' or self.ui.pw_box.text() == '' or self.ui.name_box.text() == '' or self.ui.email_box.text() == ''):
            self.ui.result.setText("id를 입력해주세요")
            return
        if(self.ui.pw_box.text() != self.ui.pw_check_box.text()):
            self.ui.result.setText("비밀번호가 다릅니다.")
            return

        self.signup.emit()
    
    def get_signup_info(self):
        signup_info = SignupInfo() 
        signup_info.id = self.ui.id_box.text()
        signup_info.pw = self.ui.pw_box.text()
        signup_info.name = self.ui.name_box.text()
        signup_info.email = self.ui.email_box.text()
        return signup_info

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        print(parent)
        self.activated.connect(parent.restore)
        menu = QtWidgets.QMenu(parent)

        openAction = menu.addAction("Open")
        openAction.triggered.connect(parent.showNormal)

        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(app.quit)
        
        self.setContextMenu(menu)



class Controller():
    def __init__(self):
        self.closed = 0
        self.main_window = MainForm()   # ui객체를 가지는것은 부담스러움     --> ui에서 controller를 붙여서 써야한다....
        self.main_window.show()         ## controller에서는 호출에대한 피드백으로 ui로 데이터 전송 
        self.login_window = LoginForm()
        self.login_window.hide()
        self.signup_window = SignUpForm()
        self.signup_window.hide()
        self.trayIcon = SystemTrayIcon(QtGui.QIcon(MAIN_ICON), self.main_window)
        self.trayIcon.hide() 


    def make_conn(self):
        self.main_window.gen_pw.connect(self.gen_pw)
        self.main_window.how_to_clicked.connect(self.open_how_to)
        self.main_window.login_clicked.connect(self.login_clicked)
        self.main_window.main_closed.connect(self.close)
        self.main_window.restore_event.connect(self.restore)
        self.main_window.show_normal.connect(self.show_normal)

        self.login_window.login_closed.connect(self.close)
        self.login_window.login.connect(self.login)
        self.login_window.make_account_clicked.connect(self.make_account_clicked)
        self.login_window.go_main_clicked.connect(self.go_main_clicked)

        self.signup_window.signup_closed.connect(self.close)
        self.signup_window.go_login_clicked.connect(self.go_login_clicked)
        self.signup_window.signup.connect(self.signup)

    def gen_pw(self):
        pw, sock = make_connection('pw')
        #화면에 pw 보여주기 gui
        
        self.main_window.show_pw(pw)### self.main_window.를 달고 다녀야 하나?
        
        waiting = threading.Thread(target=connectionStart, args=(sock,self))
        waiting.start()

    def open_how_to(self):
        webbrowser.open("https://github.com/kookmin-sw/capstone-2020-9")

    def login_clicked(self):
        self.change_window(self.main_window, self.login_window)

    def change_window(self, cur_window, next_window): # 사용자가 눈에 보이는거를 controller에서 조정 ->이러면 안됨 => view에서 처리 
        next_window.move(cur_window.x(), cur_window.y())
        cur_window.hide()
        next_window.show()

    def close(self):
        print("WindowCLoseEvent")
        self.login_window.__init__() ##생성자 는 바람직하지 않음 
        self.signup_window.__init__() ## --> init을 할때는 ui객체 생성 ->
        self.trayIcon.show()            ## clear하는 함수 생성해서 init에서도 하고 호출도 
        if( self.closed == 0 ):
            noti = threading.Thread(target=notify)
            noti.start()
        self.closed += 1

    def restore(self, reason):
        if reason == SystemTrayIcon.DoubleClick:
            self.trayIcon.hide()
            # self.showNormal will restore the window even if it was
            # minimized.
            self.main_window.show()
    
    def show_normal(self):
        self.trayIcon.hide()

    def login(self):
        sock = make_connection('login')
        login_info = self.login_window.get_login_info()
        sock.send(login_info.toJson().encode('utf-8'))
        recvData = sock.recv(1024).decode('utf-8')
        print(recvData)
        if(recvData == 'ok'): 
            self.main_window.ui.login_btn.setEnabled(False)
            self.main_window.ui.status_label.setText("연결을 기다리고 있습니다.")
            self.main_window.ui.pw_label.setText("")
            self.waiting = threading.Thread(target=connectionStart, args=(sock, self.main_window))
            self.waiting.start()
            self.change_window(self.login_window, self.main_window)
        else:
            self.login_window.ui.result.setText("올바르지 않은 ID, PW 입니다.")
    
    def make_account_clicked(self):
        self.change_window(self.login_window, self.signup_window)
    
    def go_main_clicked(self):
        self.change_window(self.login_window, self.main_window)

    def go_login_clicked(self):
        self.change_window(self.signup_window, self.login_window)
    
    def signup(self):
        sock = make_connection('signup')
        signup_info = self.signup_window.get_signup_info() 
        sock.send(signup_info.toJson().encode('utf-8'))
        recvData = sock.recv(1024).decode('utf-8')
        if(recvData == 'ok'):
            self.change_window(self.signup_window, self.login_window)
            self.signup_window.__init__()
        else:
            self.signup_window.ui.result.setText("이미 존재하는 ID 입니다.")


#fixed size = 365 305        
if __name__ == '__main__':
    WIDTH, HEIGHT = pyautogui.size()  
    MAIN_ICON = "img/Logo.png"
    print('width={0}, height={1}'.format(WIDTH, HEIGHT))

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    controller = Controller()
    controller.make_conn()

    app.exec()
    os._exit(0)
