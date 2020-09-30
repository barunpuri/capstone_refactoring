from socket import *
import threading
import time
import random
import json
import pymysql

random.seed(time.time())
lock = threading.Lock()

connected_com = dict()
connected_dev = dict()
connected_mob = dict()

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


def receive(connection_id):
    source_sock = connected_mob[connection_id]
    target_sock = connected_com[connection_id]
    while True:
        try: 
            recv_data = source_sock.recv(1024)#check source alive
            if not recv_data:    
                source_sock.close()
                break
            target_sock.send(recv_data)
        except OSError: ## except 의 종류
            ## oserror 가 아닐때도 동일한 
            target_sock.send('disconnected with other device'.encode('utf-8'))
            break
   

def check(connection_id):
    #check 의 비중보다 

    source_sock = connected_mob[connection_id]
    target_sock = connected_com[connection_id]
    receiver = threading.Thread(target=receive, args=(connection_id,), daemon=True)
    receiver.start()

    try: ## try except에 많이 넣을수록 안좋아 --> receive처럼 짜는것이 원칙 
        while True: ## 이런경우는 ㄱㅊ 은데 왠만하면 피해라
            recv_data = target_sock.recv(1024) # check target alive
            ## 한번만 쓰이는 데이터를 변수에 담지 않고 바로 쓰는게 좋음
            ##==> 그런 경우는 역할을 모를때만 그렇게 사용 
            if not recv_data:
                ## connection정리하는 역할이 겹침 => remove connection 함수 생성
                lock.acquire()
                del connected_com[connection_id]
                del connected_mob[connection_id]
                lock.release()
                target_sock.close()
                break

    except OSError : ## oserror로 들어가는 상황이 어떤거?
        ## 문제 상황에 대한 정확한 파익 필요
        ## remove connection 함수 
        lock.acquire()
        del connected_com[connection_id]
        del connected_mob[connection_id]
        lock.release()
        target_sock.close() ## target이 없을떄 문제가 안생기나? 
        source_sock.send('disconnected with other device'.encode('utf-8'))
        time.sleep(0.5)
        source_sock.close() ##reconnect? exti?


## 한 함수에서 10~20라인정도로 

def make_connection(sock):
    try: 
        recv_data = sock.recv(1024).decode('utf-8')
        conn_info = json.loads(recv_data)

        pw = connected_dev[conn_info["id"], conn_info["did"]]
        sock.send(pw.encode('utf-8'))
    except OSError:  ### 이거 ... 에러가 뭐가 나는?
        pass ## 조건이 나열될떄 고려해봐도 이건 안해도 되더라 
            ## 그게 아니면 
    # conn_info["id" | "did"]

def generate_pw(sock, mode):
## 공백도 이유가 있어야 된다. 
## 코딩 규칙 
## 내 코드 안에는 다 이래야된다 
## 하나로 결정하고 

    conn_mode = {'init':0, 'conn':1}

    pw = f'0000'
    lock.acquire()
    ## 함수로 호출한 결과 connected_com.get(pw,0) 가 명확하지 않을때는 
    ## 담아서쓰는게 좋다 
    while(pw == '0000' or connected_com.get(pw,0) != 0 ):
        pw = f'{random.randrange(1, 10**4):04}'
        # 여기서 담아서 
        #이미 쓰고 이쓴 ㄴPW  = connected_com.get(pw,0) 
        # pw가 문자열인데 비교를 0..? 
        # 다른언어를 사용하는 사람에게는 문제가 이/ㅆ을수도?
    # 조건만 줄여서 while문

    
    connected_com[pw] = sock
    connected_mob[pw] = conn_mode[mode]
    lock.release()     

    return pw

def login(login_info, sock):
    ## user단에서 pw 입력과 동시에 메모리에서 날린다
    ## 암호화 해야되는데...

    ## check 기존 유저 
    sql = 'select count(*) from user_info where id = "{}" and pw = "{}";'.format(login_info["id"], login_info["pw"])
    curs.execute(sql)
    rows = curs.fetchall()
    
    ## user 정보는 일반적으로 server에서 가지고 있음
    ## server 뜰때 

    ## 함수당 sql 문 하나만 있는게 좋다 
    ##

    
    if(rows[0][0] == 0): # count = 0
        return 'fail'.encode('utf-8')

    #if mobile
    if(login_info.get("did",0) == 0 ):  ## 변수로 지정을 해서 어느쪽인지 의미를 담아서
                                        ## 그리고 if로 분기해서 결과 보기 
        ## 함수로 빼서 
        ## 디바이스 목록을 만든다
        sql = 'select deviceName from conn_info where id = "{}";'.format(login_info["id"])
        curs.execute(sql)
        rows = curs.fetchall()
        conn_list = ''
        for r in rows: 
            if( connected_dev.get((login_info["id"],r[0]), 0) != 0 ):
                conn_list += r[0] + ','

        if(conn_list ==''): 
            conn_list = 'empty'
        
        conn = threading.Thread(target=make_connection, args=(sock,))
        conn.start()

        return conn_list.encode('utf-8')

    #if pc
    else:
        ## 장비 insert 
        ## 함수로 분리 
        ## mobile 로그인, pc로그인이 분리되어야 할것 같다. 
        sql = 'insert conn_info(id, macAddr, DeviceName) values ("{}", "{}", "{}");'.format(login_info["id"], login_info["mac"], login_info["did"])
        try:
            curs.execute(sql)
            rows = curs.fetchall()
        except: 
            ## 친절하게 알려주자
            pass

        connected_dev[login_info["id"], login_info["did"]] = generate_pw(sock, 'conn')
        return 'ok'.encode('utf-8')

    #print("login end")
    return 

def connect_w_pc(sock):
    pw = generate_pw(sock, 'init')
    sandData = pw.encode('utf-8')
    sock.send(sandData)
    return

def connect_w_mob(recv_data, sock):
    try:    
        ## 여기로 올리기
        ## send_data = 'Connected'.encode('utf-8')
        ## 조건이 다르면 같은 내용은 최소화 시킬 것
        
        if(connected_mob[recv_data] == 0):
            send_data = 'Connected'.encode('utf-8')
            sock.send(send_data)
            lock.acquire()
            connected_mob[recv_data] = 1
            lock.release()
            time.sleep(10)

        else: #connected_mob = 1
            send_data = 'Connected'.encode('utf-8')
            connected_com[recv_data].send(send_data)
            sock.send(send_data)

            lock.acquire()
            connected_mob[recv_data] = sock
            lock.release()

            checking = threading.Thread(target=check, args=(recv_data,))
            checking.start()       

        ## 조건에 따라서 달라지는게 뭔지알 수 있어야 함 
        ## if문 밖에서 connect_mob = 넣을 데이터          

    except KeyError:
        send_data = 'Invalid Password'
        sock.send(send_data.encode('utf-8'))

    except OSError: 
        send_data = 'Invalid Password'
        
        sock.send(send_data.encode('utf-8'))
        ## 연결 끊는거 가져다 쓰기 
        lock.acquire()
        del connected_mob[recv_data]
        del connected_com[recv_data]
        lock.release()
    return

def dist(sock):
    while True:
        recv_data = sock.recv(1024).decode('utf-8')
        if(recv_data == ''): break
        print("flag: {}".format(recv_data))

        if( recv_data == 'com' ): # from com 
            connect_w_pc(sock)
            ##의미없는 공백 제거 

        elif( recv_data == 'login' ):
            recv_data = sock.recv(1024).decode('utf-8')
            login_info = json.loads(recv_data)
            print("login {}".format(recv_data))

            response = login(login_info, sock)
            sock.send(response)
##길어서 분리는 함수로 빼기

        elif( recv_data == 'signup'):
            recv_data = sock.recv(1024).decode('utf-8')
            print("signup {}",format(recv_data))
            signup_info = json.loads(recv_data)  #id, pw, name, email
            print(signup_info)
            sql = 'insert user_info(id, pw, name, email) values ("{}", "{}", "{}", "{}");'.format(signup_info["id"], signup_info["pw"], signup_info["name"], signup_info["email"])
            try:
                curs.execute(sql)
                curs.fetchall()
                sock.send('ok'.encode('utf-8'))
            except :
                sock.send('fail'.encode('utf-8'))
                continue

            print("signup end")
            break
## if문안에 너무 많은 역할을 넣지 말것

        else : # from mobile, data : password 
            connect_w_mob(recv_data, sock)

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

# exe = threading.Thread(target= run)
# exe.start()

# logging = threading.Thread(target=getLog)
# logging.start()

if __name__ == '__main__' :
    while True:
        
        print( connected_com)

        connectionSock, addr = serverSock.accept()

        print(str(addr), 'connected.')

        disting = threading.Thread(target=dist, args=(connectionSock, ))
        disting.start()

        #time.sleep(1)
        pass

    db_conn.close()

db_conn.close()



'''
main -> dist 
            -> login
                -> login
            -> sign up
            -> mobile
                -> connect_w_mob
            -> computer 
                -> connect_w_pc 


'''