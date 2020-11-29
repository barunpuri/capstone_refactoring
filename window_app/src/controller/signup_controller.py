import sys
from socket import *
sys.path.append("./model")
if __name__ == '__main__':
    sys.path.append("./../model")
from signup_model import SignupInfo

from configparser import ConfigParser

parser = ConfigParser()
parser.read('config.ini')

def make_connection(): 
    clientSock = socket(AF_INET, SOCK_STREAM)
    clientSock.connect((parser.get('server', 'local_ip'), parser.getint('server', 'port')))  

    print('접속 완료')

    sendData = sendData = parser.get('reserved', 'signup')
    clientSock.send(sendData.encode('utf-8'))
    print(sendData)
    return clientSock # 

def send_signup_info(sock, id, pw, name, email):
    signup_info = SignupInfo(id, pw, name, email) 
    sock.send(signup_info.toJson().encode('utf-8'))
    recvData = sock.recv(1024).decode('utf-8')
    return recvData