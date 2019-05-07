# -*- coding:utf-8 -*-  
from socket import *
import shlex
import os
import threading
import sys
import glob
import time
import platform
import datetime

SERVER_PORT = 7734

def getPrivateIP():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def uploadListen():
    upload_socket = socket(AF_INET,SOCK_STREAM)
    upload_ip = ''
    upload_socket.bind((upload_ip,upload_port))
    while True:
        upload_socket.listen(3)
        clientsocket, clientaddr = upload_socket.accept()
        upload_thread = threading.Thread(target = buildConnection, args = (clientsocket, clientaddr))
        upload_thread.start()
    upload_thread.join()
    upload_socket.close()
    


def buildConnection(peer_socket, address):
    data = peer_socket.recv(1024)
    parameter = shlex.split(data)
    command = parameter[0]
    title = parameter[1]

    filename = title
    if command == 'GET': 
        files = glob.glob('*.txt')
        # files = glob.glob("client1\*")
        if filename in files:
            msg = ''
            peer_socket.send(msg)
            real_file = open(filename,"r")
            data = real_file.read(1024)
            while data:
                peer_socket.send(data)
                data = real_file.read(1024)
            real_file.close()
        else:
            print('file not found')
    peer_socket.close()
    sys.exit(0)


def addFile(server_IP):
    # os.system('ping www.google.com -c 3')
    clientsocket = socket(AF_INET, SOCK_STREAM)
    clientsocket.connect((server_IP,SERVER_PORT))
    global hostname
    # hostname = gethostname()
    hostname = getPrivateIP()
    ip = gethostbyname(hostname)
    file_title = raw_input('Enter the title: ')
    msg = 'ADD ' + str(file_title) + '\nHOST: ' + str(hostname) + '\nPort: ' + str(upload_port) + '\n' 
    if_passwd = raw_input('Do you want to add passward?(y/n)')
    if if_passwd == 'y':
        password = raw_input('Enter the password: ')
        msg += str(password)
    else:
        msg += 'nopassword'
    sendRequest(msg,clientsocket)

    # peer_socket = socket(AF_INET, SOCK_STREAM)
    # peer_socket.connect((server_IP, 8888))
    # command_message = 'autodownload ' + file_title + '\nHost: ' + str(hostname) + str(upload_port) + '\n'
    #     # message = 'GET ' + file_title + '\nHost: ' + str(peer_name) + '\n'
    # peer_socket.send(command_message)
    # peer_socket.close()
    
    

def listFile(server_IP):
    clientsocket = socket(AF_INET, SOCK_STREAM)
    clientsocket.connect((server_IP,SERVER_PORT))
    global hostname
    # hostname = gethostname()
    hostname = getPrivateIP()
    msg = 'LIST all available file\nHOST: ' + str(hostname) + '\nPort: ' + str(upload_port) + '\n'
    sendRequest(msg,clientsocket)

def lookupFile(server_IP):
    clientsocket = socket(AF_INET, SOCK_STREAM)
    clientsocket.connect((server_IP,SERVER_PORT))
    global hostname
    # hostname = gethostname()
    hostname = getPrivateIP()
    file_title = raw_input('Enter the title: ')
    msg = 'LOOKUP ' + str(file_title) + '\nHost: ' + str(hostname) + '\nPort: ' + str(upload_port) + '\n'
    sendRequest(msg,clientsocket)

def sendRequest(msg,clientsocket):
    clientsocket.send(msg)
    response = clientsocket.recv(1024)
    print('response from server :')
    print(str(response))


def menu():
    print('*******************Select option*******************')
    print('1. add file')
    print('2. list files')
    print('3. lookup file')
    print('4. download file')
    print('*******************Select option*******************')
    return raw_input('Enter option:')


def downloadFile(server_IP):
    clientsocket = socket(AF_INET, SOCK_STREAM)
    clientsocket.connect((server_IP,SERVER_PORT))
    # peer_name = raw_input('Enter hostname of peer server[default : 127.0.0.1]: ')
    # if peer_name == '':
    #     peer_name = '127.0.0.1'
    peer_name = server_IP
    # peer_port = raw_input('Enter upload port of peer: ')
    file_title = raw_input('Enter the title: ')
    ##find if port is available

    #check system password
    system_password = raw_input('pleasw enter system password:\n')
    msg = 'checksystempassword ' + system_password + '\n' + file_title
    clientsocket.send(msg)
    back_sys_passwd_flag = clientsocket.recv(1024)
    if back_sys_passwd_flag == 'file not found':
        print('file not exist')
        return 0

    if back_sys_passwd_flag == 'yes':
        pass
    else:
        print('password wrong')
        return 0



    #check file password
    msg2 = 'checkpassword ' + file_title
    clientsocket.send(msg2)
    # clientsocket.send(file_title)
    back_passwd_flag = clientsocket.recv(1024)
    if back_passwd_flag == 'nopassword':
        # print('wrong password')
        check_password = ''
    else: 
        check_password = str(raw_input('please enter file password:\n'))
    if check_password == back_passwd_flag or back_passwd_flag == 'nopassword':
        peer_socket = socket(AF_INET, SOCK_STREAM)
        peer_socket.connect((peer_name,int(8888)))   
        if file_title is not None:
            message = 'GET ' + file_title + '\nHost: ' + str(peer_name) +'\n' + str(8888) + '\n'
        peer_socket.send(message)
        data = peer_socket.recv(1024)
        file_name = file_title
        with open(file_name,"w+") as file:
            while data:
                file.write(data)
                print('downloading...')
                data = peer_socket.recv(1024)
        print('download finished')
        file.close()
        peer_socket.close()
        # print('Enter option:')
        sendRequest(message,clientsocket)
        return 0




def connectToServer():
    global server_IP
    server_IP = raw_input('Enter the server IP[default : 127.0.0.1]: ')
    if server_IP == '':
        server_IP = '127.0.0.1'
    while(1):
        user_option = menu()
        if user_option == '1':
            addFile(server_IP)
        elif user_option == '2':
            listFile(server_IP)
        elif user_option == '3':
            lookupFile(server_IP)
        elif user_option == '4':
            downloadFile(server_IP)
        else:
            print('Option not found, try again')

def main():
    global upload_port
    upload_port = int(raw_input('Enter the client port: '))
    first_thread = threading.Thread(target = uploadListen)       
    first_thread.start()
    
    second_thread = threading.Thread(target = connectToServer)
    second_thread.start()
    first_thread.join()
    second_thread.join()
    
    
if __name__ == '__main__':
    main()
