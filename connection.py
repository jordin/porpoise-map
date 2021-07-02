"""
Programmer: Jordin McEachern
Program: harbour porpoise map
Created on: 2021-03-02
File: connection.py
Description: handles the serial connection
"""
import serial.tools.list_ports
import threading, sys, os
import serial

port = None
baud_rate = 115200 # default baud rate

# immediately prints a debug message
def log(msg):
    print(msg, flush=True)

def create_serial_connection():
    global port, baud_rate

    # check for user-defined com port
    if len(sys.argv) > 1:
        port = sys.argv[1]

    # check for user-defined baud rate
    if len(sys.argv) > 2:
        baud_rate = int(sys.argv[2])

    if port is None: # dynamically find an available com port
        ports = serial.tools.list_ports.comports()
        if not ports: # no ports found
            log("No available COM port found. Entering demo mode.")
            return None
        log(f"Found: {' '.join(map(lambda p: p.device, ports))}")
        port = ports[0].device
        log(f"Using {port} at {baud_rate} bits per second")
    
    # open desired serial port at the desired baud rate
    return serial.Serial(port, baud_rate)
