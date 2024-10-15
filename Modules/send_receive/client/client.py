#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq
import cv2
import numpy as np
import json
context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Do 10 requests, waiting each time for a response
while True:
    print(f"Sending request …")
    recall = False
    set_joint_0 = .30
    set_joint_1 = .30
    set_joint_2 = .30
    client_payload = {
        "recall" : recall,
        "set_joint_0" : set_joint_0,
        "set_joint_1" : set_joint_1,
        "set_joint_2" : set_joint_2,
        
    }
    m2s = json.dumps(client_payload)

    socket.send_string(m2s)

    #  Get the reply.
    message = socket.recv()
    m_dict = json.loads(message)
    buff = np.array(m_dict["img"])
    print(f" pos_0 = {m_dict["joint_0_pos"]}, pos_1 = {m_dict["joint_1_pos"]}, pos_2 = {m_dict["joint_2_pos"]} ")
    buff = buff.reshape(1, -1)
    img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
    cv2.imshow("client",img)
    exit_key_press = cv2.waitKey(1)

    if exit_key_press == ord("q"):
        break
cv2.waitKey(0)
cv2.destroyAllWindows()


