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
        self.cap = cv2.VideoCapture(0)

    def start_connection(self):
        self.keep_running = True
        self.thread = threading.Thread(target=self.thread_main)
        return True

    # return False

    def stop_connection(self):
        self.keep_running = False
        return True
    # return False
    def thread_main(self):
        asyncio.run(self.start_async())
    async def start_asnyc(self):
        while self.keep_running:    
            frame = cv2.cvtColor(self.selected_HAL.capture_image(),cv2.COLOR_HSV2RGB)
            cv2.imshow('frame',frame)
            res, im_string =cv2.imencode(".jpg",frame)
            image_base64 = base64.b64encode(im_string).decode('utf-8')
            #  Wait for next request from client
            message = self.socket.recv() 
            print(f"Received request: {message}")

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


