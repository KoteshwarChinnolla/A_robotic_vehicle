import matplotlib.pyplot as plt
import numpy as np
import heapq
import serial
import time
from PIL import Image


# arduino = serial.Serial(port='COM7', baudrate=9600, timeout=1)
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
                # print('f')
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
                # print(f'c{c}')
                send.append(f'c{c}')
            else:
                # print(f'a{a}')
                send.append(f'a{a}')

        return send
            
    def decode(self,data):
        rotate=''
        angle=0
        if(data=='f'):
            rotate=' '
            # print('sent f')
            self.sendtoarduino('f')
        else:
            angle=int(data[1:])
            if(data[0]=='c'):
                for i in range(angle//45):
                    rotate+=' r'
                    # print('sent r')
                    self.sendtoarduino('r')
            else:
                for i in range(angle//45):
                    rotate+=' l'
                    # print('sent l')
                    self.sendtoarduino('l')
        return rotate

    def sendtoarduino(self,data):
        print('sent',data)
        # arduino.write((data + '\n').encode())
        if data=='f':
            time.sleep(0.1)
        else:
            time.sleep(0.05)
# s=send_arduino()
# data = s.angles_to_send(data=['right-down', 'right-down', 'right-down', 'right-down', 'right-down', 'down', 'down', 'down', 'down', 'down', 'down', 'down', 'down', 'down'])
# for i in data:
#     sent=s.decode(i)
    # print("sent",sent)
