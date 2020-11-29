import threading
import enum
import json
import os
import pyautogui
import platform

from socket import *
from tkinter import *
from PIL import Image, ImageTk
from win10toast import ToastNotifier
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5 import QtCore

from configparser import ConfigParser

parser = ConfigParser()
parser.read('config.ini')

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
    img_files = ['./../img/click.png', './../img/left.png', './../img/right.png', './../img/locked.png', './../img/unlocked.png']
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
    mode, x_ratio, y_ratio = '','',''
    try:
        mode, x_ratio, y_ratio = recvData.split(',')

        point_x = WIDTH * float(x_ratio) #ratio 범위 check 
        point_y = HEIGHT * float(y_ratio)
    except ValueError as m:    
        print(recvData)        
        print(m) 

        print("좌표 : {}, {}".format(point_x,point_y) )
        if(mode == Mode.CLICK.value):       # value -> 문자로 가져가야 하는가
            pyautogui.click(x=point_x, y=point_y) 
        elif(mode == Mode.LEFT.value):
            pyautogui.press('left')
        elif(mode == Mode.RIGHT.value):
            pyautogui.press('right')
        elif(mode == Mode.LOCK.value):
            pass
        elif(mode == Mode.UNLOCK.value):
            pass
        # action 이라는 class가 있고 
        # 여러 곳에서 이런 구조를 보여준다고 하면 
        # action에 따라서 상속 구조를 가져가는것이 가장 적합

        p = threading.Thread(target = make_popup_image, args=(int(mode),), daemon=True )
        p.start()


def make_connection(): # request ...같은 이름으로 바꾸기 
    clientSock = socket(AF_INET, SOCK_STREAM)
    clientSock.connect((parser.get('server', 'local_ip'), parser.getint('server', 'port')))     ## file로 처리 
    #clientSock.connect((parser.get('server', 'ip'), parser.getint('server', 'port')))    
        # ip, port ->  ini 파일로...
    #꼭 connection을 매번 연결 해야하는가?
    # 한번 연결한거를 계속 쓰면? 
    # client, server가 여러 socket을 갖는것은 부적절 
    # client에서 server로 보내는것을 thread로 한다면!
        # 그 thread가 길어진다면 괜찮은데 
        # 그게 아니면 별로 

    print('접속 완료')

    sendData = 'com'
    clientSock.send(sendData.encode('utf-8'))

    password = clientSock.recv(1024).decode('utf-8')

    #화면에 비밀번호 보여주기 
    print("pw : " + password)
    return clientSock, password 
    

def connectionStart(sock): # 항상 좋게 끝난다고 가정
    #연결 성공 
    while True: 
        recvData = sock.recv(1024).decode('utf-8')
        if( recvData == parser.get('reserved', 'Connected') ):
            print(recvData)
            return 'Connected'

def handling_start(sock, signal):
    handling = threading.Thread(target=handling_PC, args=(sock, signal))
    handling.start()

def handling_PC(sock, signal):
    # 좌표값 
    recvData = ''
    while True: # socket 에러 처리 필요 
        recvData = sock.recv(1024).decode('utf-8')
        if( recvData == 'disconnected with other device'): 
            signal.disconnected.emit()
            sock.close()
            break # 재접속 여부 확인 
        elif( recvData == parser.get('reserved', 'closed') ):
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


