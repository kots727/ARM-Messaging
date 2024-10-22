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

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    while not ret:
        print("failed to read")
        ret, frame = cap.read()
    res, im_string =cv2.imencode(".jpg",frame)
    image_base64 = base64.b64encode(im_string).decode('utf-8')
    #  Wait for next request from client
    message = socket.recv() 
    print(f"Received request: {message}")

    #  Do some 'work'

    joint_0_pos = .3
    joint_1_pos = .1
    joint_2_pos = .2
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
    socket.send_string(m2s)