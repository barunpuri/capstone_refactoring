import threading
import enum
import json
import os
import pyautogui
import platform
import uuid

from socket import *
from tkinter import *
from PIL import Image, ImageTk
from win10toast import ToastNotifier
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5 import QtCore

sys.path.append("./model")
if __name__ == '__main__':
    sys.path.append("./../model")
from login_model import LoginInfo
from signup_model import SignupInfo

WIDTH, HEIGHT = pyautogui.size() 


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
        if(mode == Mode.CLICK.value):       # value -> 문자로 가져가야 하는가
            pyautogui.click(x=point_x, y=point_y)   # 
        elif(mode == Mode.LEFT.value):
            pyautogui.press('left')
        elif(mode == Mode.RIGHT.value):
            pyautogui.press('right')
        elif(mode == Mode.LOCK.value):  # 의미가 있긴있는데 ...
            pass                            # point on screen 함수에 따르면 없어도 될거 같은데-> 삭제! 
        elif(mode == Mode.UNLOCK.value):    # action 이라는 class가 있고 
            pass                            # 여러 곳에서 이런 구조를 보여준다고 하면 
                                            # action에 따라서 상속 구조를 가져가는것이 가장 적합

        p = threading.Thread(target = make_popup_image, args=(int(mode),), daemon=True )
        p.start()

    except ValueError as m:     # 57 로 옮길 필요 있음
        print(recvData)         # 코드의 이해도를 위해 
        print(m)                # try block 한정 필요 
                                # value error 
                                # + thread 에서 error 발생가능하면
                                # 74번 라인만 처리

def make_connection(id): # request ...같은 이름으로 바꾸기 
    port = 8081

    clientSock = socket(AF_INET, SOCK_STREAM)
    clientSock.connect(('127.0.0.1', port))     ## file로 처리 
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
        return clientSock, password 
                                    
    
    elif( id == 'login' or id == 'signup'):
        sendData = id
        clientSock.send(sendData.encode('utf-8'))
        
        return clientSock # 

def connectionStart(sock): # 항상 좋게 끝난다고 가정
    #연결 성공 
    while True: 
        recvData = sock.recv(1024).decode('utf-8')
        if( recvData == 'Connected' ):
            print(recvData)
            return 'Connected'

def handling_start(sock):
    handling = threading.Thread(target=handling_PC, args=(sock))
    handling.start()

def handling_PC(sock):
    # 좌표값 
    recvData = ''
    while True: # socket 에러 처리 필요 
        recvData = sock.recv(1024).decode('utf-8')
        if( recvData == 'test' ) : # test코드 삭제 
            continue
        elif( recvData == 'disconnected with other device'): 
            '''signal
                if( res == 'disconnected with other device'):
                    QDialog.ui.status_label.setText('연결이 종료되었습니다. \n다시 연결하려면 번호를 다시 생성해 주세요')
                    QDialog.ui.pw_label.setText('')
            ''' 
            sock.close()
            break # 재접속 여부 확인 
        elif( recvData == 'closed' ):
            sock.close()
            break

        print('입력 :', recvData)  # '0, 0.7, 0.5'
        
        p = threading.Thread(target = point_on_screen, args=(recvData,), daemon=True )
        p.start()
    
    return recvData

def notify():
    if( platform.system() == 'Windows' and platform.release() == '10'):
        toaster = ToastNotifier()
        toaster.show_toast("Touch On Screen", "Program is running in System Tray~", icon_path="./../img/Logo.ico", duration=4, threaded=True)

def send_login_info(sock, id, pw):  # login info 의 변수를 외부에서 접근을 막 해도 되느냐 
    login_info = LoginInfo()        # private , public 개념 x 
    login_info.id = id              # get set 이 없으면 접근 자제
    login_info.pw = pw              # 외부 접근이 필요하면 get set 생성 or *생성자에서 초기화가 좋음*
    login_info.did = gethostname()  # 나중에 값을 바꾸려면 set추가 
    login_info.mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
    sock.send(login_info.toJson().encode('utf-8'))
    recvData = sock.recv(1024).decode('utf-8')
    return recvData

def send_signup_info(sock, id, pw, name, email):
    signup_info = SignupInfo() 
    signup_info.id = id
    signup_info.pw = pw
    signup_info.name = name
    signup_info.email = email
    sock.send(signup_info.toJson().encode('utf-8'))
    recvData = sock.recv(1024).decode('utf-8')
    return recvData

class Signal(QObject):
    restore = pyqtSignal()
    basic = pyqtSignal(int, int)
    login = pyqtSignal(int, int)
    signup = pyqtSignal(int, int)
    close = pyqtSignal()
    quit = pyqtSignal()
    loggined = pyqtSignal(socket)
    tray = pyqtSignal()

    def __init__(self, parent=None):
        self.closed = 0
        QObject.__init__(self, parent)


'''
code review 
    문제 제시 사람
    문제 해결 사람
    서기 
-> 문제 발생 ->서기 : issue 등록 -> 문제 해결 -> 잘 됐으면 confirm / 안되면 다시 



27일까지... 고치기
- controller 3개로 분리
12월 4일 4시 20분 다시 미팅 
'''