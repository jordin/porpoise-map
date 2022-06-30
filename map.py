"""
Programmer: Jordin McEachern
Program: harbour porpoise map
Created on: 2021-02-24
File: map.py
Description: handles the gui
"""
import LatLon23
from PIL import ImageTk
import threading, sys, os
import tkinter as tk
import connection as conn
import math
import time

# map image dimensions
img_width = 1300
img_height = 825

# hydrophone position
# hydrophone_x = 430
# hydrophone_y = 530

parrsboro = True
if len(sys.argv) > 1:
    parrsboro = sys.argv[1] != '1'

if (parrsboro):
    map_image = "img/map_parrsboro.png"
    hydrophone_x = 450
    hydrophone_y = 400
    hydrophone_lat_lon = LatLon23.LatLon(LatLon23.Latitude(45.36705242670009), LatLon23.Longitude(-64.41993457568921))
    metre_to_pixel_multiplier = 159 / 100
else:
    map_image = "img/map_grand_passage.png"
    hydrophone_x = 450
    hydrophone_y = 300
    hydrophone_lat_lon = LatLon23.LatLon(LatLon23.Latitude(44.291236), LatLon23.Longitude(-66.343494))

    metre_to_pixel_multiplier = 155 / 100

# porpoise position 
default_porpoise_x = 800 
default_porpoise_y = 500

# porpoise position (initially off screen)
porpoise_x = -100
porpoise_y = -100
porpoise_lat_lon = None

ser = conn.create_serial_connection()

if ser is None:
    porpoise_x = default_porpoise_x
    porpoise_y = default_porpoise_y

porpoise_r = "?"
porpoise_theta = "?"

# immediately prints a debug message
def log(msg):
    print(msg, flush=True)

def format_coord(coord):
    return f'{int(coord.degree)}°{int(abs(coord.minute))}\'{abs(coord.second):.3f} {coord.get_hemisphere()}'

def format_latlon(latlon):
    return f'{format_coord(latlon.lat)}, {format_coord(latlon.lon)}'.replace("-", "") # - is handled by displaying the hemisphere

# update the map window
def process_updates(root, state):
    global img_width, img_height, ser, hydrophone_lat_lon, porpoise_lat_lon, porpoise_r, porpoise_theta
    # create window with appropriate size
    canvas = tk.Canvas(root, width = img_width, height = img_height)
    canvas.pack()

    background = ImageTk.PhotoImage(file = map_image)
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
            hydrophone_text = None
            porpoise_text = None
            # update porpoise icon position
            porpoise = canvas.create_image(porpoise_x, porpoise_y, image = porpoise_img, anchor="center")

            if porpoise_lat_lon is not None:
                hydrophone_text = canvas.create_text(4, 4, fill="white", font = "Arial 24", text=f"Hydrophone: {format_latlon(hydrophone_lat_lon)}", anchor="nw")
                porpoise_text = canvas.create_text(4, 44, fill="white", font = "Arial 24", text=f"Porpoise: {int(porpoise_r)}m @ {int(math.degrees(porpoise_theta))}° ({format_latlon(porpoise_lat_lon)})", anchor="nw")

            root.after_idle(state["next"])

            yield

            canvas.delete(porpoise)
            if range_text is not None:
                canvas.delete(range_text)
            if theta_text is not None:
                canvas.delete(theta_text)
            if hydrophone_text is not None:
                canvas.delete(hydrophone_text)
            if porpoise_text is not None:
                canvas.delete(porpoise_text)
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

    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    w = img_width
    h = img_height

    # # calculate x and y coordinates for the Tk root window
    x = (ws) - (w)
    # # set the dimensions of the screen 
    # # and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, x, 0))
    root.mainloop()

def handle_serial_connection():
    global ser
    if (ser is None):
        on_update(0, 121, 2.52)
        while (True):
            time.sleep(0.01)
    else:
        read_serial_connection(ser)

    # close application when serial port closes    
    os._exit(1)

def on_update(i, r, theta):
    global porpoise_x, porpoise_y, hydrophone_x, hydrophone_y, metre_to_pixel_multiplier, porpoise_r, porpoise_theta, hydrophone_lat_lon, porpoise_lat_lon
    porpoise_x = hydrophone_x + metre_to_pixel_multiplier * (r * math.cos(theta))
    porpoise_y = hydrophone_y - metre_to_pixel_multiplier * (r * math.sin(theta))
    porpoise_r = r
    porpoise_theta = theta
    porpoise_lat_lon = hydrophone_lat_lon.offset(theta, r / 1000)

def read_serial_connection(ser):
    ser.write(b'\x03\n') # CONTROL+C
    ser.write(b'\x03\n') # CONTROL+C

    ser.write(b'./config-ip.sh\n')

    ser.write(b'./run_trac_tdoa\n')
    
    while (ser.is_open):
        # read in all data received
        while (ser.in_waiting):
            line = ser.readline()
            log(f"Raw: {line}")
            
            try:
                params = line.split()

                if (len(params) == 3):
                    i = int(params[0])
                    theta = float(params[1])
                    r = float(params[2])

                    if (r == 500):
                        r = 40

                    on_update(i, r, math.radians(theta))
            except:
                pass

        time.sleep(0.01)

    ser.is_open = False

try:
    show()
except:
    os._exit(1)