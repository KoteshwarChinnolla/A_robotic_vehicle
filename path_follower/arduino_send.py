import matplotlib.pyplot as plt
import numpy as np
import heapq
import serial
import time
from PIL import Image

import os
from dotenv import load_dotenv
load_dotenv()

arduino_port = os.getenv("ARDUINO_PORT")   # e.g. "COM7"
baudrate = os.getenv("ARDUINO_BAUDRATE")   # e.g. "9600"

if arduino_port is not None:
    baudrate = int(baudrate) if baudrate is not None else 9600
    arduino = serial.Serial(
        port=arduino_port,
        baudrate=baudrate,
        timeout=1
    )

class send_arduino:
    def angles_to_send(self,data):
        # print(data)
        dec = {
            "up":90,
            "down":270,
            "left":0,
            "right":180,
            "right-up":135,
            "left-up":45,
            "left-down":315,
            "right-down":225
        }
        send=[]
        pa=ca=angle=a=c=0
        p="left"
        for i in data:
            if(p==i):
                send.append("f")
                continue
            ca=dec[i]
            angle=ca-pa
            if(angle>=0):
                a=angle
            else:
                a=360-abs(angle)
            c=360-a
            pa=ca
            p=i
            if(c<a):
                send.append(f'c{c}')
            else:
                send.append(f'a{a}')

        return send
            
    def decode(self,data):
        rotate=''
        angle=0
        if(data=='f'):
            rotate=' '
            self.sendtoarduino('f')
        else:
            angle=int(data[1:])
            if(data[0]=='c'):
                for i in range(angle//45):
                    rotate+=' r'
                    self.sendtoarduino('r')
            else:
                for i in range(angle//45):
                    rotate+=' l'
                    self.sendtoarduino('l')
        return rotate

    def sendtoarduino(self,data):
        print('sent',data)
        if arduino_port is not None:
            arduino.write((data + '\n').encode())
        if data=='f':
            time.sleep(0.1)
        else:
            time.sleep(0.05)
# s=send_arduino()
# data = s.angles_to_send(data=['right-down', 'right-down', 'right-down', 'right-down', 'right-down', 'down', 'down', 'down', 'down', 'down', 'down', 'down', 'down', 'down'])
# for i in data:
#     sent=s.decode(i)
    # print("sent",sent)
