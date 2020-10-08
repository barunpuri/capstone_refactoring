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
        # os error 말고 다른 error 발생 가능? 
        # 있으면 남기기 
        # oserror -> 아는 error 는 warning
        # 모르는 error : error로 처리 (5단계)
        #except 의 종류, 메세지 신경써서 남기기 

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

def check_login_info(login_info): #에러 나면 어떻게해? => db 쓰는쪽 다 처리 하기 에러 ! 
    sql = 'select count(*) from user_info where id = "{}" and pw = "{}";'.format(login_info["id"], login_info["pw"])
    curs.execute(sql)
    rows = curs.fetchall() # [0][0] 을 붙이고 rows의 이름을 바꾸기 
    return rows[0][0]!=0

def make_device_list(login_info):
    sql = 'select deviceName from conn_info where id = "{}";'.format(login_info["id"]) # caching.... 되도록 (알아보기)
    curs.execute(sql)
    rows = curs.fetchall()
    conn_list = ''
    for r in rows: 
        if(connected_dev.get((login_info["id"], r[0]), 0) != 0): #=> 지금 가지고 있는 애들을 주고 살아 있는 애들만 가져와야 함 
            conn_list += r[0] + ','     # db 찾아보면 해결 할수도? 

    if(conn_list ==''): # not conn_list 
        conn_list = 'empty' #mobile에 empty로 전달... => error code(숫자)로 주는것이 바람직 
    
    return conn_list

def add_pc(login_info):
    sql = 'insert conn_info(id, macAddr, DeviceName) values ("{}", "{}", "{}");'.format(login_info["id"], login_info["mac"], login_info["did"])
    try:
        curs.execute(sql)
        curs.fetchall()
    except Exception as m : 
        print(m)

def login(login_info, sock):
    is_exist = check_login_info(login_info) #is_exist 없애고 check_login_info의 이름 바꾸기 

    if(not is_exist): 
        sock.send('fail'.encode('utf-8'))
        return 

    response_message = ''
    #if mobile
    is_mobile = login_info.get("did", 0) == 0 # device type == mobile? 
    if(is_mobile):                              #login info.devicetype으로 가져다 쓸수 있도록... 
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

def mobile_connect(pw, data): ## data = 0 :init | 1 : touch | sock : conn # 동사로 시작 
    lock.acquire()
    connected_mob[pw] = data
    lock.release()

def connect_w_mob(recv_data, sock): # from ~ 
    try:    
        send_data = 'Connected'.encode('utf-8')
        sock.send(send_data)
        
        if(connected_mob[recv_data] == 0): #더 많이 일어나는 것을 위로 가는게 좋음  # if 문 안쓰고 해결...? 
            mobile_connect(recv_data, 1)
        else: #connected_mob = 1
            connected_com[recv_data].send(send_data)
            mobile_connect(recv_data, sock)
            checking = threading.Thread(target=check_alive, args=(recv_data,))
            checking.start()       

            return "connected_by_pw"
        return ''
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
            #원하는 정보인지 확인하는 작업 필요 
            login_info = json.loads(sock.recv(1024).decode('utf-8')) # login info class를 만들어서 json에서 받은 정보를 서버가 활용할 수 있게 변경해서 들고 다니게 
                                                                    # id, pw, device type, device id, mac 
            print(login_info)                                       # 사용자가 준 데이터를 프로그램에서 사용 할 수 있는 데이터로 변경하여 사용 
            login(login_info, sock)

        elif(recv_data == 'signup'):
            #원하는 정보인지 확인하는 작업 필요 
            signup_info = json.loads(sock.recv(1024).decode('utf-8'))  #id, pw, name, email
            print(signup_info)
            try:
                add_user(signup_info)
            except :
                sock.send('fail'.encode('utf-8')) # fail 의 종류 구분 필요 
                continue
            sock.send('ok'.encode('utf-8'))
            print("signup end")
            break

        else : # from mobile, data : password 
            phase = connect_w_mob(recv_data, sock)
            if(phase == 'connected_by_pw'):
                break

#중복 처리 어떻게? duplicated id 검사 
# return 친절... 해야된다! 
# log라도 친절하게 찍기 


def add_user(signup_info):
    ## 여러 실패 케이스르 만들어서 어떤 error를 뿌리는지 확인 
    sql = 'insert user_info(id, pw, name, email) values ("{}", "{}", "{}", "{}");'.format(signup_info["id"], signup_info["pw"], signup_info["name"], signup_info["email"])
    curs.execute(sql)
    curs.fetchall()
    
#mysql 5.7.22 

# MySQL Connection 연결
                                ## db 에러 처리 필요 
db_conn = pymysql.connect(host='database-1.cgi3kozgpark.ap-northeast-2.rds.amazonaws.com', 
port = 3306, user='admin', password='**', db='capstone', charset='utf8',autocommit=True)

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
connected_com[f'0000'] = -1
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


#connectino을 관리하는 애가 있고 
# 상속 받아서 mobile conne
        #   comput conne
