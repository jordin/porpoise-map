"""
Programmer: Jordin McEachern
Program: harbour porpoise map
Created on: 2021-02-24
File: map.py
Description: handles the gui
"""
from PIL import Image, ImageTk
import serial.tools.list_ports
import threading, sys, os
import tkinter as tk
import serial
import time

port = None
baud_rate = 115200 # default baud rate

# map image dimensions
img_width = 1353
img_height = 861

# hydrophone position
hydrophone_x = 700
hydrophone_y = 600

# porpoise position
porpoise_x = 800 
porpoise_y = 500

# pending outgoing messages
send_queue = []

# check for user-defined com port
if len(sys.argv) > 1:
    port = sys.argv[1]

# check for user-defined baud rate
if len(sys.argv) > 2:
    baud_rate = int(sys.argv[2])

# train position (initially off screen)
pos_x = -100
pos_y = -100
direction = 'n'

# immediately prints a debug message
def log(msg):
    print(msg, flush=True)

# update the map window
def process_updates(root, state):
    global pos_x, pos_y, direction, ser, img_width, img_height
    # create window with appropriate size
    canvas = tk.Canvas(root, width = img_width, height = img_height)
    canvas.pack()

    background = ImageTk.PhotoImage(file = "img/map.png")
    canvas.create_image(img_width / 2, img_height / 2, image = background, anchor="center")

    hydrophone = ImageTk.PhotoImage(file = "img/hydrophone.png")
    canvas.create_image(hydrophone_x, hydrophone_y, image = hydrophone, anchor="center")

    porpoise = ImageTk.PhotoImage(file = "img/porpoise.png")
    canvas.create_image(porpoise_x, porpoise_y, image = porpoise, anchor="center")

    canvas.create_line(hydrophone_x, hydrophone_y, porpoise_x, porpoise_y, width = 4)

    try:
        while True:
            # update train icon position
            # trainimg = ImageTk.PhotoImage(file = f"img/train-{direction}.png")
            # train = canvas.create_image(pos_x, pos_y, image = trainimg, anchor = "center")
        
            root.after_idle(state["next"])
            yield
            # canvas.delete(train)
    except: # window closes (CONTROL+C or X button)
        # close serial port
        # ser.close()
        os._exit(1)

# create the map window
def show():
    root = tk.Tk()
    root.title('Harbour Porpoise Map')
    root.resizable(False, False)
    # root.attributes("-fullscreen", True)
    state = {}
    state["next"] = process_updates(root, state).__next__

    root.after(1, state["next"])

    root.mainloop()

try:
    show()
except:
    os._exit(1)
