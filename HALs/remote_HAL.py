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
import base64
import asyncio
class remote_HAL(HAL_base):
    def __init__(self):
        super().__init__()
        self.execute = False
        self.set_joint = [0,0,0]
        self.img = 0
        self.get_joint = [0,0,0]

    def start_arm(self):
        self.context = zmq.Context()

        #  Socket to talk to server
        print("Connecting to hello world server…")
        self.socket = self.context.socket(zmq.REQ)
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
        if self.img != 0:
            hsv_image = cv2.cvtColor(self.img, cv2.COLOR_RGB2HSV)
            return hsv_image
        else: 
            return "no image"
    def start_asnyc(self):
        while self.keep_running:
            print(f"Sending request …")
          

            client_payload = {
                "execute" : self.execute,
                "set_joint_0" : self.set_joint[0],
                "set_joint_1" : self.set_joint[1],
                "set_joint_2" : self.set_joint[2],
                
            }
            m2s = json.dumps(client_payload)

            self.socket.send_string(m2s)
            self.execute = False
            #  Get the reply.
            message = self.socket.recv()
            
            m_dict = json.loads(message)
            img_data = base64.b64decode(m_dict['img'])
            np_img = np.frombuffer(img_data, dtype=np.uint8)    
            print(f" pos_0 = {m_dict["joint_0_pos"]}, pos_1 = {m_dict["joint_1_pos"]}, pos_2 = {m_dict["joint_2_pos"]} ")
            self.img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            self.get_joint[0] = m_dict["joint_0_pos"]
            self.get_joint[1] = m_dict["joint_1_pos"]
            self.get_joint[2] = m_dict["joint_2_pos"]
        
    

