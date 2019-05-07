# -*- coding:utf-8 -*-  
from socket import *
import sys
import os
import threading
import shlex
import time

SERVER_PORT = 7734
BACKUP_SERVER_PORT = 9999
SYSTEM_PASSWORD = 123456

def getPrivateIP():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

private_ip = getPrivateIP()

class Peer:
    def __init__(self,hostname='None',upload_port='None'):
        self.hostname = hostname
        self.upload_port = upload_port

        
class File:
    def __init__(self,file_title='None',file_source=Peer()):
        self.file_title = file_title
        self.file_source = file_source


class Node:
    
    def __init__(self,data):
        self._data = data
        self._next = None

    def getData(self):
        return self._data

    def getNext(self):
        return self._next

    def setNext(self,newnext):
        self._next = newnext

class LinkedList:

    def __init__(self):
        self._head = None

    def __iter__(self):
        current = self._head
        while current is not None:
            yield current
            current = current.getNext()

    def add(self,item):
        temp = Node(item)
        temp.setNext(self._head)
        self._head = temp

    def search(self,item):
        current = self._head
        flag = False
        while current != None and not flag:
                if current.getData() == item:
                    flag = True
                else:
                    current = current.getNext()

        return flag

    def size(self):
        current = self._head
        count = 0
        while current != None:
            count = count + 1
            current = current.getNext()

        return count

    def remove(self,item):
        current = self._head
        previous = None
        flag = False
        while not flag:
            if current.getData() == item:
                flag = True
            else:
                previous = current
                current = current.getNext()
        if previous == None:
            self._head = current.getNext()
        else:
            previous.setNext(current.getNext())


def buildConnection(peer_socket, address):
    while True:
        global response
        response = peer_socket.recv(1024)

        if len(response) == 0:
            peer_socket.close()
            return
        parameter = response.split(' ')
        
        command = parameter[0]
        #########
        # for i in parameter:
        #     print(i)
        # print('\n')
        #########
        if command=='ADD':
            print(response)
            writeLog(response)
            addFile(response, peer_socket)
        elif command=='LOOKUP':
            print(response)
            writeLog(response)
            lookupFile(response, peer_socket)
        elif command=='LIST':
            print(response)
            writeLog(response)
            listFile(peer_socket)
        elif command=='DEL':
            print(response)
            writeLog(response)
            deletePeer(response, peer_socket)
        elif command == 'GET':
            print(response)
            writeLog(response)
            downloadFile(response, peer_socket)
        elif command == 'DELETE':
            print(response)
            writeLog(response)
            deleteFile(response, peer_socket)
        elif command == 'checkpassword':
            judgeFilePasswd(response, peer_socket)
        elif command == 'checksystempassword':
            judgeSystemPasswd(response, peer_socket)
        elif command == 'unlock':
            unlockFileSystem(response, peer_socket)
        elif command == 'lock':
            lockFileSystem(response, peer_socket)
        else:#file name
            judgeSystemPasswd(command,peer_socket)




peer_library = LinkedList()
file_library = LinkedList()
password_library = {} #dictionary

def judgeFilePasswd(response,peer_socket):
    arr = shlex.split(response)
    file_title = arr[1]
    for i in password_library:
        
        # print(i)
        print(password_library.get(i))
    flag = 'nopassword'
    password = str(password_library.get(str(file_title)))

    if password == flag:
        flag = 'nopassword'
    else:
        flag = str(password)
    # print(flag)
    peer_socket.send(flag)

def judgeSystemPasswd(response, peer_socket):
    arr = shlex.split(response)
    # for i in arr:
        # print(i)
    client_given_passwd = arr[1]
    file_title = arr[2]
    file_number = file_library.size()
    file_exist_flag = 0
    for active_file in file_library:
            # print(active_file.getData().file_title)
            if str(active_file.getData().file_title) == file_title:
                file_exist_flag += 1
    if file_exist_flag != 1:
        peer_socket.send('file not found')
        return 0
    # print('\n')
    # print(client_given_passwd)
    # print(SYSTEM_PASSWORD)
    flag = 'yes'
    if str(client_given_passwd) == str(SYSTEM_PASSWORD):
        flag = 'yes'
    else:
        flag = 'no'
    # print(flag)
    peer_socket.send(flag)

def unlockFileSystem(response, peer_socket):
    arr = shlex.split(response)
    decryFile()
    flag = 'unlock_finished'
    peer_socket.send(flag)

def lockFileSystem(response, peer_socket):
    arr = shlex.split(response)
    encryFile()
    flag = 'lock_finished'
    peer_socket.send(flag)

def addFile(response, peer_socket):
    # decryFile()
    arr = shlex.split(response)
    
    file_title = arr[1]
    hostname = arr[3]
    upload_port = arr[5]
    password = arr[6]

    new_peer = Peer(hostname,upload_port)
    if new_peer not in peer_library:
        peer_library.add(new_peer)

    new_file = File(file_title, new_peer)
    if new_file not in file_library:       
        file_library.add(new_file)
    msg = 'success\n' +str(new_file.file_title) + ' '+str(hostname) + ' ' + str(upload_port)
    peer_socket.send(msg)
    
    

    download_socket = socket(AF_INET, SOCK_STREAM)
    download_socket.connect((hostname,int(upload_port)))   
    if file_title is not None:
        message = 'GET ' + file_title + '\nHost: ' + str(hostname) + '\n'
    download_socket.send(message)
    data = download_socket.recv(1024)
    file_name = file_title
    with open(file_name,"w+") as file:
        while data:
            file.write(data)
            data = download_socket.recv(1024)
    
    file.close()

    if password == 'nopassword':
        password_library[file_title] = 'nopassword'
    else:
        password_library[file_title] = password
    download_socket.close()
    informBackupServer(file_title)
    # encryFile()

def informBackupServer(file_title):
    backup_socket = socket(AF_INET, SOCK_STREAM)
    backup_socket.connect((backup_server_ip,int(9999)))   
    msg = 'backup ' + file_title
    backup_socket.send(msg)
    data = backup_socket.recv (1024)


def lookupFile(response,peer_socket):
    arr = shlex.split(response)
    
    file_title = arr[1]
    # print(file_title)
    msg = '\n\nfile not found\n\n'
    if file_library.size() > 0:
        for active_file in file_library:
            # print(active_file.getData().file_title)
            if str(active_file.getData().file_title) == file_title:
                msg = '\n\n'
                msg += 'file found\n'
                msg += 'file name / file host name / file host port\n'
                
                # msg = 'File '+str(active_file.getData().file_title) + ' ' + str(active_file.getData().file_source.hostname)+' '+str(active_file.getData().file_source.upload_port)
                msg += str(active_file.getData().file_title) + ' ' + str(active_file.getData().file_source.hostname)+' '+str(active_file.getData().file_source.upload_port)
                
    msg += '\n\n'
    peer_socket.send(msg)

def listFile(peer_socket):
    
    msg = 'not found\n'
    if file_library.size() > 0:
        # msg = 'success\n'
        msg = '\n\n'
        msg += 'file name / file host name / file host port\n'
        for active_file in file_library:
        #    msg += 'File '+str(active_file.getData().file_title) + ' '+str(active_file.getData().file_source.hostname) + ' ' + str(active_file.getData().file_source.upload_port) + '\n'  
            msg += str(active_file.getData().file_title) + ' '+str(active_file.getData().file_source.hostname) + ' ' + str(active_file.getData().file_source.upload_port) + '\n'  
    
    msg += '\n\n'
    peer_socket.send(msg)


def downloadFile(response,peer_socket):
    # os.sleep(10)
    # decryFile()
    arr = shlex.split(response)
    file_title = arr[1]
    upload_port = arr[-1]
    msg = '\n\nfile not found\n\n'
    for active_file in file_library:
        if str(active_file.getData().file_title) == file_title:
            msg = '\n\nYou have downloaded the file successfully\n\n'
    peer_socket.send(msg)
    # os.sleep(20)
    # encryFile()

def deleteFile(response, peer_socket):
    decryFile()
    arr = shlex.split(response)
    file_title = arr[1]
    for active_file in file_library:
        if active_file.getData().file_title == file_title:
            file_library.remove(active_file.getData())
    msg = 'rm ' + file_title
    os.system(msg)
    encryFile()
    backmsg = '' + file_title +' has been deleted'
    peer_socket.send(backmsg)


def encryFile():
    os.system('mkdir mount')
    if file_library.size() > 0:
        for active_file in file_library:
            msg = './movefile '  
            msg += str(active_file.getData().file_title)
            msg += ' mount' 
            # msg = './encryption '
            # msg += str(active_file.getData().file_title)
            # msg += ' encrypted.zip 123456' 
            os.system(msg)
        runDedup() #dedup before move into folder
    os.system('./encryption mount encrypted.zip 123456')
    os.system('mkdir mount')
    os.system('./movefile mount encrypted.zip')
    os.system('mkdir fusemount')
    os.system('./worm mount fusemount ')
    os.system('rm -rf mount')


def decryFile():
    os.system('fusermount -u fusermount')
    os.system('./movefile fusemount/encrypted.zip .')
    os.system('./decryption encrypted.zip 123456')
    for active_file in file_library:
        msg = './movefile mount/' 
        msg += str(active_file.getData().file_title)
        msg += ' .' 
        os.system(msg)
    os.system('rm -rf fusemount')
    os.system('rm -rf mount')
    

def runDedup():
    os.system('python2 dedup.py  mount')

def writeLog(string):
    msg = '\n' + string
    now_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    f = open("log.txt", "a+")
    msg += now_time
    f.write(msg)
    f.write("\n")

def deletePeer(response,peer_socket):
    arr = shlex.split(response)    
    
    hostname = arr[3]
    upload_port = arr[5]    
    for active_file in file_library:
        if active_file.getData().file_source.upload_port == upload_port:
            file_library.remove(active_file.getData())
    for active_peer in peer_library:
        if active_peer.getData().upload_port == upload_port:
            peer_library.remove(active_peer.getData())       
    msg = ''
    msg += 'success\n'    
    peer_socket.send(msg)

def main():
    global backup_server_ip
    backup_server_ip = raw_input('Enter the backup server IP:')
    encryFile()
    upload_socket = socket(AF_INET,SOCK_STREAM)
    global upload_ip
    upload_ip = ''
    upload_socket.bind((upload_ip,SERVER_PORT))
    while True:
        upload_socket.listen(3)
        clientsocket, clientaddr = upload_socket.accept()
        upload_thread = threading.Thread(target = buildConnection, args = (clientsocket, clientaddr))
        upload_thread.start()
    upload_thread.join()
    upload_socket.close()

if __name__ == '__main__':  
    main()
