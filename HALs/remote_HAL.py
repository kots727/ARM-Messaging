from HALs.HAL_base import HAL_base
#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq
import cv2
import numpy as np
import json
import threading
import socket
import base64

import asyncio
class remote_HAL(HAL_base):
    def __init__(self):
        super().__init__()
        self.set_joint_val = [[0,False],[0,False],[0,False]]
        self.read_from = 0
        self.img = np.zeros((256, 256, 3), dtype=np.uint8)
        self.joint_val = [0,0,0]

    def start_arm(self):
        self.context = zmq.Context()

        #  Socket to talk to server
        print("Connecting to hello world server…")
        self.socket = self.context.socket(zmq.REQ)
        self.socket_identity = socket.gethostname()
        self.socket.connect("tcp://localhost:5555")
        self.keep_running = True
        self.thread = threading.Thread(target=self.thread_main)
        self.thread.start()


    def thread_main(self):
        asyncio.run(self.start_async())

    def stop_arm(self):
        # global sim
        self.keep_running = False
    def get_arm_cam_img_hsv(self):
        hsv_image = cv2.cvtColor(self.img, cv2.COLOR_RGB2HSV)
        return hsv_image
    
    def set_joint(self, joint_index, joint_angle):
        self.set_joint_val[joint_index] = [joint_angle, True]
        pass
    def get_joint(self, joint_index):
        return self.joint_val[joint_index]
    def joint_count(self):
        return 3
    async def start_async(self):
        while self.keep_running:
            print(f"Sending request …")
          

            client_payload = {
                "set_joint_0" : self.set_joint_val[0],
                "set_joint_1" : self.set_joint_val[1],
                "set_joint_2" : self.set_joint_val[2],
                "id": self.socket_identity
            }
            m2s = json.dumps(client_payload)

            self.socket.send_string(m2s)
            self.set_joint_val = [[0,False],[0,False],[0,False]]
            #  Get the reply.
            message = self.socket.recv()
            
            m_dict = json.loads(message)
            print("1")
            img_data = base64.b64decode(m_dict['img'])
            print("1")
            np_img = np.frombuffer(img_data, dtype=np.uint8)    
            print("1") 
            print(f" pos_0 = {m_dict["joint_0_pos"]}, pos_1 = {m_dict["joint_1_pos"]}, pos_2 = {m_dict["joint_2_pos"]} ")
            self.img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            self.joint_val[0] = m_dict["joint_0_pos"]
            self.joint_val[1] = m_dict["joint_1_pos"]
            self.joint_val[2] = m_dict["joint_2_pos"]
        
    

