"""
Programmer: Jordin McEachern
Program: harbour porpoise map
Created on: 2021-02-24
File: map.py
Description: handles the gui
"""
from PIL import Image, ImageTk
import threading, sys, os
import tkinter as tk
import connection as conn
import math
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
default_porpoise_x = 800 
default_porpoise_y = 500

# porpoise position (initially off screen)
porpoise_x = -100
porpoise_y = -100

# Map scale
metre_to_pixel_multiplier = 0.0712867647

# pending outgoing messages
send_queue = []

# check for user-defined com port
if len(sys.argv) > 1:
    port = sys.argv[1]

# check for user-defined baud rate
if len(sys.argv) > 2:
    baud_rate = int(sys.argv[2])

ser = conn.create_serial_connection()

if ser is None:
    porpoise_x = default_porpoise_x
    porpoise_y = default_porpoise_y

porpoise_r = "?"
porpoise_theta = "?"

# immediately prints a debug message
def log(msg):
    print(msg, flush=True)

# update the map window
def process_updates(root, state):
    global pos_x, pos_y, img_width, img_height, ser, r, theta
    # create window with appropriate size
    canvas = tk.Canvas(root, width = img_width, height = img_height)
    canvas.pack()

    background = ImageTk.PhotoImage(file = "img/map.png")
    canvas.create_image(img_width / 2, img_height / 2, image = background, anchor="center")

    hydrophone = ImageTk.PhotoImage(file = "img/hydrophone.png")
    canvas.create_image(hydrophone_x, hydrophone_y, image = hydrophone, anchor="center")

    # canvas.create_line(hydrophone_x, hydrophone_y, porpoise_x, porpoise_y, width = 4)

    t = threading.Thread(target = handle_serial_connection)
    t.daemon = True
    t.start()

    porpoise_img = ImageTk.PhotoImage(file = "img/porpoise.png")

    try:
        while True:
            range_text = None
            theta_text = None
            # update porpoise icon position
            porpoise = canvas.create_image(porpoise_x, porpoise_y, image = porpoise_img, anchor="center")

            if porpoise_r != "?":
                range_text = canvas.create_text(4, 4, fill="black", font = "Arial 24", text=f"Range: {int(porpoise_r)}m", anchor="nw")
                theta_text = canvas.create_text(4, 44, fill="black", font = "Arial 24", text=f"Angle: {int(math.degrees(porpoise_theta))}°", anchor="nw")

            root.after_idle(state["next"])

            yield

            canvas.delete(porpoise)
            if range_text is not None:
                canvas.delete(range_text)
            if theta_text is not None:
                canvas.delete(theta_text)
    except: # window closes (CONTROL+C or X button)
        # close serial port
        if ser is not None:
            ser.close()
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

def handle_serial_connection():
    global ser
    if (ser is None):
        on_update(0, 921, 2.52)
        while (True):
            time.sleep(0.01)
    else:
        read_serial_connection(ser)

    # close application when serial port closes    
    os._exit(1)

def on_update(i, r, theta):
    global porpoise_x, porpoise_y, hydrophone_x, hydrophone_y, metre_to_pixel_multiplier, porpoise_r, porpoise_theta
    porpoise_x = hydrophone_x + metre_to_pixel_multiplier * (r * math.cos(theta))
    porpoise_y = hydrophone_y - metre_to_pixel_multiplier * (r * math.sin(theta))
    porpoise_r = r
    porpoise_theta = theta

def read_serial_connection(ser):
    # ser.write("./map")
    while (ser.is_open):
        # read in all data received
        while (ser.in_waiting):
            line = ser.readline()
            log(f"Raw: {line}")
            
            params = line.split()

            i = int(params[0])
            r = float(params[1])
            theta = float(params[2])

            on_update(i, r, theta)

        time.sleep(0.01)

    ser.is_open = False

try:
    show()
except:
    os._exit(1)