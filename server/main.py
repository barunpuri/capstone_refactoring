from socket import *
import threading
import time
import random
import json
import pymysql


# ##지우기 
# def getLog():
#     while True:
#         now = time.localtime()
#         print("%02d:%02d:%02d" % ((now.tm_hour+9)%24, now.tm_min, now.tm_sec) + str(connected_com) + str(connected_mob))
#         time.sleep(300)

# def run():
#     while True: 
#         try:
#             s = input()
#             exec(s)
#         except error as m:
#             print(m)

def disconnect(connection_id):
    lock.acquire()
    del connected_com[connection_id]
    del connected_mob[connection_id]
    lock.release()

def receive(connection_id):
    source_sock = connected_mob[connection_id]
    target_sock = connected_com[connection_id]
    while True:
        try: 
            recv_data = source_sock.recv(1024)#check source alive
            if (not recv_data):    
                source_sock.close()
                break
            target_sock.send(recv_data)
        except OSError: 
            target_sock.send('disconnected with other device'.encode('utf-8'))
            break

def check_alive(connection_id):
    source_sock = connected_mob[connection_id]
    target_sock = connected_com[connection_id]
    receiver = threading.Thread(target=receive, args=(connection_id, ), daemon=True)
    receiver.start()

    while(True):
        try : 
            recv_data = target_sock.recv(1024)
            if not recv_data:
                disconnect(connection_id)
                target_sock.close()
                break

        except OSError : 
            disconnect(connection_id)
            target_sock.close() ## target이 없을떄 문제가 안생기나? 
            source_sock.send('disconnected with other device'.encode('utf-8'))
            source_sock.close() ##reconnect? exti?
            break

def make_connection(sock):
    try: 
        recv_data = sock.recv(1024).decode('utf-8')
        conn_info = json.loads(recv_data)

        pw = connected_dev[conn_info["id"], conn_info["did"]]
        sock.send(pw.encode('utf-8'))
    except OSError as m:  
        print(m)

def generate_pw(sock, mode):
    conn_mode = {'init':0, 'conn':1}
    pw = f'0000'
    is_pw_exist = connected_com.get(pw,0) != 0 # exist : not 0 | not exist : 0
    lock.acquire()
    while(is_pw_exist):
        pw = f'{random.randrange(1, 10**4):04}'
        is_pw_exist = connected_com.get(pw,0) != 0 
    connected_com[pw] = sock
    connected_mob[pw] = conn_mode[mode]
    lock.release()     

    return pw

def check_login_info(login_info):
    sql = 'select count(*) from user_info where id = "{}" and pw = "{}";'.format(login_info["id"], login_info["pw"])
    curs.execute(sql)
    rows = curs.fetchall()
    return rows[0][0]!=0

def make_device_list(login_info):
    sql = 'select deviceName from conn_info where id = "{}";'.format(login_info["id"])
    curs.execute(sql)
    rows = curs.fetchall()
    conn_list = ''
    for r in rows: 
        if(connected_dev.get((login_info["id"], r[0]), 0) != 0):
            conn_list += r[0] + ','

    if(conn_list ==''): 
        conn_list = 'empty'
    
    return conn_list

def add_pc(login_info):
    sql = 'insert conn_info(id, macAddr, DeviceName) values ("{}", "{}", "{}");'.format(login_info["id"], login_info["mac"], login_info["did"])
    try:
        curs.execute(sql)
        curs.fetchall()
    except Exception as m : 
        print(m)

def login(login_info, sock):
    is_exist = check_login_info(login_info)

    if(not is_exist): 
        sock.send('fail'.encode('utf-8'))
        return 

    response_message = ''
    #if mobile
    is_mobile = login_info.get("did", 0) == 0
    if(is_mobile):  
        response_message = make_device_list(login_info)
        conn = threading.Thread(target=make_connection, args=(sock, ))
        conn.start()
    else:
        add_pc(login_info)
        connected_dev[login_info["id"], login_info["did"]] = generate_pw(sock, 'conn')
        response_message = 'ok'

    sock.send(response_message.encode('utf-8'))
    
def connect_w_pc(sock):
    pw = generate_pw(sock, 'init')
    sandData = pw.encode('utf-8')
    sock.send(sandData)
    return

def mobile_connect(pw, data): ## data = 0 :init | 1 : touch | sock : conn
    lock.acquire()
    connected_mob[pw] = data
    lock.release()

def connect_w_mob(recv_data, sock):
    try:    
        send_data = 'Connected'.encode('utf-8')
        sock.send(send_data)
        
        if(connected_mob[recv_data] == 0):
            mobile_connect(recv_data, 1)
        else: #connected_mob = 1
            connected_com[recv_data].send(send_data)
            mobile_connect(recv_data, sock)
            checking = threading.Thread(target=check_alive, args=(recv_data,))
            checking.start()       

    except KeyError:
        send_data = 'Invalid Password'
        sock.send(send_data.encode('utf-8'))

    except OSError: 
        send_data = 'Invalid Password'
        sock.send(send_data.encode('utf-8'))
        disconnect(recv_data)
    
def dist(sock):
    while True:
        recv_data = sock.recv(1024).decode('utf-8')
        if(recv_data == ''): break
        print("flag: {}".format(recv_data))

        if(recv_data == 'com'): # from com 
            connect_w_pc(sock)

        elif(recv_data == 'login'):
            login_info = json.loads(sock.recv(1024).decode('utf-8'))
            print(login_info)
            login(login_info, sock)

        elif(recv_data == 'signup'):
            signup_info = json.loads(sock.recv(1024).decode('utf-8'))  #id, pw, name, email
            print(signup_info)
            try:
                add_user(signup_info)
            except :
                sock.send('fail'.encode('utf-8'))
                continue
            sock.send('ok'.encode('utf-8'))
            print("signup end")
            break

        else : # from mobile, data : password 
            connect_w_mob(recv_data, sock)

def add_user(signup_info):
    sql = 'insert user_info(id, pw, name, email) values ("{}", "{}", "{}", "{}");'.format(signup_info["id"], signup_info["pw"], signup_info["name"], signup_info["email"])
    curs.execute(sql)
    curs.fetchall()
    
#mysql 5.7.22 

# MySQL Connection 연결
db_conn = pymysql.connect(host='database-1.cgi3kozgpark.ap-northeast-2.rds.amazonaws.com', 
port = 3306, user='admin', password='puri142857', db='capstone', charset='utf8',autocommit=True)

# # Connection 으로부터 Cursor 생성
curs = db_conn.cursor()
 
# # SQL문 실행
# sql = "select * from customer"
# curs.execute(sql)
 
# # 데이타 Fetch
# rows = curs.fetchall()
# print(rows)     # 전체 rows
# # print(rows[0])  # 첫번째 row: (1, '김정수', 1, '서울')
# # print(rows[1])  # 두번째 row: (2, '강수정', 2, '서울')
 
# Connection 닫기
# db_conn.close()

port = 8081
serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', port))
serverSock.listen(1)

random.seed(time.time())
lock = threading.Lock()

connected_com = dict()
connected_dev = dict()
connected_mob = dict()

# exe = threading.Thread(target= run)
# exe.start()

# logging = threading.Thread(target=getLog)
# logging.start()

if __name__ == '__main__' :
    while True:
        print(connected_com)
        connectionSock, addr = serverSock.accept()
        print(str(addr), 'connected.')
        disting = threading.Thread(target=dist, args=(connectionSock, ))
        disting.start()

    db_conn.close()
db_conn.close()
