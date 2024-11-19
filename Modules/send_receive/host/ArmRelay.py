#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
import cv2
import numpy as np
import json 
import base64
import threading
import asyncio

from Controllers import FollowClaw
from nicegui import ui
from Modules.send_receive.host.RelayBase import RelayBase
from Controllers.Controller import Controller
from Controllers.FollowClaw import coordinate_input
from HALs.HAL_base import HAL_base
from Vision.ColorObjectIdentifier import ColorObjectIdentifier

class ArmRelay(RelayBase):
    def __init__(self, selected_HAL: HAL_base, **kwargs):
        super().__init__(**kwargs)
        self.selected_HAL = selected_HAL
        self.keep_running = False
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")
        self.connections ={}
        self.connection_names=[]

        self.toggle2 = ui.toggle(self.connections, value=0)
        
        ui.run()

    def start_connection(self):
        self.keep_running = True

        self.thread = threading.Thread(target=self.thread_main)
        self.thread.start()
        return True

    # return False

    def stop_connection(self):
        self.keep_running = False
        return True
    # return False
    def thread_main(self):
        print("x")
        asyncio.run(self.start_async())

    
    async def start_async(self):
        while self.keep_running:    
            print("testss")
            frame = cv2.cvtColor(self.selected_HAL.capture_image(),cv2.COLOR_HSV2RGB)
            res, im_string =cv2.imencode(".jpg",frame)
            image_base64 = base64.b64encode(im_string).decode('utf-8')
            #  Wait for next request from client
            print("primed to receive request")
            message = self.socket.recv() 
            print(f"Received request: {message}")
            m_dict = json.loads(message)
            set_joint_l = [0,0,0]
            set_joint_l[0] = m_dict["set_joint_0"]
            set_joint_l[1] = m_dict["set_joint_1"]
            set_joint_l[2] = m_dict["set_joint_2"]
            connection_id = m_dict["id"]
            if self.connections.__len__()>0:
                if connection_id == self.connections[self.toggle2.value]:
                    for x in range(3):
                        if set_joint_l[x][1]:
                            self.selected_HAL.set_joint(x,set_joint_l[x][0])
            else:
                for x in range(3):
                    if set_joint_l[x][1]:
                        self.selected_HAL.set_joint(x,set_joint_l[x][0])
            if connection_id not in self.connections.values():
                self.connections[connection_id] = self.connections.__len__()-1
                self.connection_names.append(connection_id)
            

            #  Do some 'work'

            joint_0_pos = self.selected_HAL.get_joint(0)
            joint_1_pos = self.selected_HAL.get_joint(1)
            joint_2_pos = self.selected_HAL.get_joint(2)
            #  Send reply back to client
            print(image_base64)
            print(type(image_base64))
            host_payload ={
                "img" : image_base64,
                "joint_0_pos" : joint_0_pos,
                "joint_1_pos" : joint_1_pos,
                "joint_2_pos" : joint_2_pos
            }
            m2s= json.dumps(host_payload)
            self.socket.send_string(m2s)


