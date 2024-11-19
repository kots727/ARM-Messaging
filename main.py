from typing import List
import argparse
import numpy as np
import cv2
import json
import ctypes  # For alerts

from HALs.HAL_base import HAL_base
from Vision.VisualObjectIdentifier import VisualObjectIdentifier
from Controllers.Controller import Controller
from Modules.server.ServerBase import ServerBase

from Vision.ColorObjectIdentifier import ColorObjectIdentifier
from Controllers.FollowLargestObjectControler import FollowLargestObjectControler
from Controllers.FollowClaw import FollowClawController

import subprocess
import sys

# Configuration
# these are the default values, they are saved in a file called config.json that is ignored by git.
# if you add or rename parameters, please increment config_version for everything to work properly. 
config = {
    "config_version" : 1,
    "use_simulator" : True,
    "use_physical" : False,
    "use_app" : False,
    "as_host": True,
    "use_server" : True,
    "use_twitch" : False,
    "open_startup_page" : False,
    "twitch_id" : "NONE",
    "twitch_secret" : "NONE",
    "twitch_channel_name" : "ucscarm"
}

selected_HAL : HAL_base = None
selected_object_identifier : VisualObjectIdentifier = None
selected_controler : Controller = None
selected_server : ServerBase = None

# ARG parsing
parser = argparse.ArgumentParser()

# Function to handle the custom logic for --mode
def twitch_channel_name_type(value):
    if value is None:
        return "ucscarm"
    try:
        return str(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid twitch channel value: {value}")

# Adding optional argument
parser.add_argument("-s", "--simulator", help = "Use the Coppeliasim hardware interface.")
parser.add_argument("-p", "--physical", help = "Use the Physical hardware interface.")
parser.add_argument("--use_app", help = "Use the app as the controler.")
parser.add_argument("--disable_server", action='store_true', help = "Disable the locally hosted server.")
parser.add_argument('--twitch_chat', nargs='?', const="ucscarm", type=twitch_channel_name_type, help='If passed in, will connect to provided twitch channel (default is ucscarm).')


def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)
def SaveConfig():
    json_object = json.dumps(config, indent=4) 
    with open("config.json", "w") as outfile:
        outfile.write(json_object)

try:
    with open('config.json', 'r') as openfile:
        json_object = json.load(openfile)
        if json_object["config_version"] < config["config_version"]:
            print("Invalid Config, creating new file")
            Mbox('Invalid Arm Config', 'The config file used was old, so a new one was created. Be sure to update any parameters then relaunch.', 1)
            SaveConfig()
            sys.exit()
        config = json_object
except:
    print("No config.json found, it has been created.")
    SaveConfig()


# Read arguments from command line
args = parser.parse_args()
if args.simulator:
    config["use_simulator"] = True
if args.physical:
    config["use_simulator"] = True
if args.disable_server:
    config["use_server"] = False
if args.twitch_chat is not None:
    config["use_twitch"] = True
    selected_twitch_channel = args.twitch_chat
if args.use_app:
    config["use_app"] = True

# HAL stuff
selected_HAL : HAL_base = None

if config["use_simulator"]:
    from HALs.sim_HAL import sim_HAL
    selected_HAL = sim_HAL()
elif config["use_physical"]:
    from HALs.physical_HAL import physical_HAL
    selected_HAL = physical_HAL()
    # selected_HAL = physical_HAL
    
# vision stuff
lower_blue = np.array([100, 150, 50])
upper_blue = np.array([140, 255, 255])
lower_red = np.array([0, 150, 50])
upper_red = np.array([40, 255, 255])
selected_object_identifier: VisualObjectIdentifier = ColorObjectIdentifier(lower_blue, upper_blue)

# controler stuff
selected_controler: Controller = None

selected_app = None
if config["use_app"]:
    # Kivy opens the window if this is imported, thus why it is here.
    from Modules.App.App import App
    selected_object_identifier: ColorObjectIdentifier = ColorObjectIdentifier(lower_red, upper_red)
    selected_controler = FollowClawController(selected_HAL,selected_object_identifier)    
    selected_app = App(selected_controler, selected_HAL, selected_object_identifier)

# Server setup
if config["use_server"]:
    from Modules.server.server import Server
    selected_server: ServerBase = Server(selected_controler, selected_HAL, selected_object_identifier)

# Twitch setup
if config["use_twitch"]:
    from Modules.twitch.TwitchChat import TwitchChat
    selected_twitch = TwitchChat()
    if config["twitch_id"] == "NONE":
        print("Please set twitch_id to a valid twitch_id to use the twitch chat reader")
    elif config["twitch_secret"] == "NONE":
        print("Please set twitch_secret to a valid twitch secret to use the twitch chat reader")
    else:
        selected_twitch = TwitchChat(config["twitch_id"], config["twitch_secret"])

#Relay setup
if config["as_host"]:
    from Modules.send_receive.host.ArmRelay import ArmRelay
    selected_relay = ArmRelay(selected_HAL)


print('              Selected HAL: ' + selected_HAL.__class__.__name__)
print('Selected object_identifier: ' + selected_object_identifier.__class__.__name__)
print('        Selected controler: ' + selected_controler.__class__.__name__)
print('           Selected server: ' + selected_server.__class__.__name__)
print('              Selected app: ' + selected_app.__class__.__name__)

keep_running = True

if __name__ == "__main__":
    # ----------------- SETUP -----------------
    print("Arm startup")

    # Remote API init
    selected_HAL.start_arm()    

    print("Controler Startup")
    # Start the Controler
    if selected_controler is not None:
        selected_controler.start()
    
    # Connect to twitch
    if config["use_twitch"]:
        if 'selected_twitch_channel' in locals():
            selected_twitch.connect_to_twitch(selected_twitch_channel)
        else:
            selected_twitch.connect_to_twitch(config["twitch_channel_name"])
        
    # ----------------- END SETUP -----------------
    
    # ----------------- MAIN PROGRAM LOOP -----------------
    if config["use_server"]:
        print("Server Startup")
        selected_server.start_server()
    
    if config["as_host"] and not config["use_server"] and not config["use_app"]:
        print("Relay Started")
        selected_relay.start_connection()

    if config["use_app"]:
        try:
            selected_app.start_app()
        except KeyboardInterrupt:
                keep_running = False
        
    if not config["use_server"] and not config["use_app"]:
        while keep_running:
            print("Arm is running, press 'q' or ctrl-c to quit")
            try:
                user_value = input("Enter a command: ")
                if user_value == 'q':
                    keep_running = False
            except KeyboardInterrupt:
                keep_running = False
            
        
    # ----------------- END MAIN PROGRAM LOOP -----------------

    # ----------------- CLEAUP / SHUTDOWN -----------------

    print("Arm shutdown")
    keep_running = False
    if config["use_twitch"]:
        selected_twitch.stop_twitch_chat()
    if selected_server is not None:
        selected_server.stop_server()
    if selected_controler is not None:
        selected_controler.stop()
    selected_HAL.stop_arm()
    
    print("Arm shutdown complete")
    
    # Reopen Startup page
    if config["open_startup_page"]:
        subprocess.Popen(['python', 'ArmTeam/startup.py'])

    # ----------------- END CLEAUP / SHUTDOWN -----------------
