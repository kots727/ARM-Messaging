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

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        print("failed to read")
    cv2.imshow('frame',frame)
    res, im_string =cv2.imencode(".jpg",frame)
    im_string = im_string.tolist()
    #  Wait for next request from client
    message = socket.recv() 
    print(f"Received request: {message}")

    #  Do some 'work'

    joint_0_pos = .3
    joint_1_pos = .1
    joint_2_pos = .2
    #  Send reply back to client
    host_payload ={
        "img" : im_string,
        "joint_0_pos" : joint_0_pos,
        "joint_1_pos" : joint_1_pos,
        "joint_2_pos" : joint_2_pos
    }
    m2s= json.dumps(host_payload)
    socket.send_string(m2s)
    exit_key_press = cv2.waitKey(1)

    if exit_key_press == ord("q"):
        break
cap.release()
cv2.waitKey(0)
cv2.destroyAllWindows()
