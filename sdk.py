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
server_client_port = 8888

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
        upload_socket.listen(1)
        clientsocket, clientaddr = upload_socket.accept()
        upload_thread = threading.Thread(target = buildConnection, args = (clientsocket, clientaddr))
        upload_thread.start()
        # auto_thread = threading.Thread(target = autoDetect, args = (clientsocket, clientaddr))
        # auto_thread.start()
    upload_thread.join()
    upload_socket.close()
    

def buildConnection(peer_socket, address):
    data = peer_socket.recv(1024)
    parameter = shlex.split(data)
    
    command = parameter[0]
    title = parameter[1]
    auto_port = parameter[-1]
    filename = title
    if command == 'GET': 
        serversocket = socket(AF_INET, SOCK_STREAM)
        serversocket.connect((server_IP,SERVER_PORT))
        temp1 = 'unlock'
        serversocket.send(temp1)
        back1 = serversocket.recv(1024)
        if back1 == 'unlock_finished':

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
        temp2 = 'lock'
        serversocket.send(temp2)
        back2 = serversocket.recv(1024)
        if back2 == 'lock_finished':
            serversocket.close()
        # else:
        #     print('file not found')
        
        

    if command == 'autodownload':
        auto_Download(server_IP, auto_port)
    peer_socket.close()
    sys.exit(0)


def auto_Download(server_IP, peer_port):
    clientsocket = socket(AF_INET, SOCK_STREAM)
    clientsocket.connect((server_IP,SERVER_PORT))
    peer_name = raw_input('Enter hostname of peer server[default : 127.0.0.1]: ')
    if peer_name == '':
        peer_name = '127.0.0.1'
    # peer_port = raw_input('Enter upload port of peer: ')
    file_title = raw_input('Enter title: ')
    temp = '' + peer_port
    clientsocket.send(temp)
    back = clientsocket.recv(1024)
    if back == '0':
        print('\n\n\nport not found\n\n\n')
        return 0
    peer_socket = socket(AF_INET, SOCK_STREAM)
    peer_socket.connect((peer_name,int(peer_port)))   
    if file_title is not None:
        message = 'GET ' + file_title + '\nHost: ' + str(peer_name) + '\n'
    peer_socket.send(message)
    data = peer_socket.recv(1024)
    file_name = file_title
    with open(file_name,"w+") as file:
        while data:
            file.write(data)
            print('downloading...')
            time.sleep(0.2)
            data = peer_socket.recv(1024)
    print('download finished')
    file.close()
    peer_socket.close()
    print('Enter option:')
    sendRequest(message,clientsocket)
    return 0

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

def deleteFile(server_IP):
    clientsocket = socket(AF_INET, SOCK_STREAM)
    clientsocket.connect((server_IP,SERVER_PORT))
    global hostname
    hostname = getPrivateIP()
    file_title = raw_input('Enter the title which you want to delete: ')
    msg = 'DELETE ' + str(file_title) + '\nHost: ' + str(hostname) + '\nPort: ' + str(upload_port) + '\n'
    sendRequest(msg,clientsocket)

def delete_peer(server_IP):
    clientsocket = socket(AF_INET, SOCK_STREAM)
    clientsocket.connect((server_IP,SERVER_PORT))
    global hostname
    # hostname = gethostname()
    hostname = getPrivateIP()
    msg = 'DEL Client\nHOST: ' + str(hostname) + '\nPort: ' + str(upload_port) + '\n'
    sendRequest(msg,clientsocket)

def sendRequest(msg,clientsocket):
    clientsocket.send(msg)
    response = clientsocket.recv(1024)
    print('response from server :')
    print(str(response))




def menu():
    print('*******************Select option*******************')
    
    print('1. list files')
    print('2. lookup file')
    print('3. delete file')
    print('*******************Select option*******************')
    return raw_input('Enter option:')

def connectToServer():
    global server_IP
    server_IP = raw_input('Enter the server IP[default : 127.0.0.1]: ')
    if server_IP == '':
        server_IP = '127.0.0.1'
    while(1):
        user_option = menu()
        if user_option == '1':
            listFile(server_IP)
        elif user_option == '2':
            lookupFile(server_IP)
        elif user_option == '3':
            deleteFile(server_IP)
        else:
            print('Option not found, try again')

def main():
    global upload_port
    upload_port = server_client_port
    first_thread = threading.Thread(target = uploadListen)       
    first_thread.start()
    
    second_thread = threading.Thread(target = connectToServer)
    second_thread.start()
    first_thread.join()
    second_thread.join()
    
    
if __name__ == '__main__':
    main()
