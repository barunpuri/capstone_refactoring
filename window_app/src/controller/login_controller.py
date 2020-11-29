import sys
import uuid
from socket import *
sys.path.append("./model")
if __name__ == '__main__':
    sys.path.append("./../model")
from login_model import LoginInfo

from configparser import ConfigParser

parser = ConfigParser()
parser.read('config.ini')

def make_connection(): 
    clientSock = socket(AF_INET, SOCK_STREAM)
    clientSock.connect((parser.get('server', 'local_ip'), parser.getint('server', 'port')))  

    print('접속 완료')
                                
    sendData = parser.get('reserved', 'login')
    clientSock.send(sendData.encode('utf-8'))
    print(sendData)
    return clientSock # 

def send_login_info(sock, id, pw):
    did = gethostname()
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
    login_info = LoginInfo(id, pw, did, mac)
    sock.send(login_info.toJson().encode('utf-8'))
    recvData = sock.recv(1024).decode('utf-8')
    return recvData
