from socket import *
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5 import QtCore

class Signal(QObject):
    restore = pyqtSignal()
    basic = pyqtSignal(int, int)
    login = pyqtSignal(int, int)
    signup = pyqtSignal(int, int)
    close = pyqtSignal(QtCore.QEvent)
    quit = pyqtSignal()
    loggined = pyqtSignal(socket)
    tray = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self, parent=None):
        self.closed = 0
        QObject.__init__(self, parent)

'''
code review 
    문제 제시 사람
    문제 해결 사람
    서기 
-> 문제 발생 ->서기 : issue 등록 -> 문제 해결 -> 잘 됐으면 confirm / 안되면 다시 
'''