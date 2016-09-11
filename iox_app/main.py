#!/usr/bin/python
"""
ioxduino is an IOx Proof of Concept to integrate a Cisco Router with an Arduino Microcontroller.

ioxduino is provided as proof of concept code illustrating how such an application could be built
leveraging IOx and an Arduino.

In ioxduino, the external sensor running on the Arduino is a basic push button.
When the button is pressed the Arduino sends an event out the serial interface.
The serial interface on the Arduino is connected to a Serial Interface on the IOx Router,
which is monitored by the IOx application code.

When a button press is detected by the IOx application it updates a log that is available
with a basic REST API call.

This program is the main python code that runs as a PaaS application on an IOx host
that monitors the incoming Serial data, and provides a basic REST API for accessing
details on the events.

Details on the full project available at https://github.com/imapex/ioxduino

"""

import serial
import time
import json
import signal
import threading
import os
from datetime import datetime
from wsgiref.simple_server import make_server


# Handle standard signals
def _sleep_handler(signum, frame):
    print "SIGINT Received. Stopping CAF"
    raise KeyboardInterrupt


def _stop_handler(signum, frame):
    print "SIGTERM Received. Stopping CAF"
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, _stop_handler)
signal.signal(signal.SIGINT, _sleep_handler)

# Port and Host informaiton for the WSGI HTTP Server
PORT = 6000
HOST = "0.0.0.0"


# A relatively simple WSGI application. It will print out the
# alerts that have been logged by the application
def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    ret = json.dumps(alerts)
    return ret


# List to store instances of the alerts
alerts = []


class SerialThread(threading.Thread):
    def __init__(self):
        super(SerialThread, self).__init__()
        self.name = "SerialThread"
        self.setDaemon(True)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        serial_dev = os.getenv("HOST_DEV1")
        if serial_dev is None:
            serial_dev = "/dev/cu.usbserial"

        sdev = serial.Serial(port=serial_dev, baudrate=9600)
        sdev.bytesize = serial.EIGHTBITS                        # number of bits per bytes
        sdev.parity = serial.PARITY_NONE                        # set parity check: no parity
        sdev.stopbits = serial.STOPBITS_ONE                     # number of stop bits
        sdev.timeout = 5

        print "Serial:  %s\n" % sdev
        sdev.write("Starting Up: %s \r\n" % sdev)

        while True:
            if self.stop_event.is_set():
                break
            # Check if there is incoming data waiting on the serial line
            while sdev.inWaiting() > 0:
                # There is something strange with the decoding that happens
                # of incoming data running on an IOx device (at least 819)
                # For now using simpler code to just see if an event was triggered
                # And log that, rather than grabbing data from the event
                print("Incoming Data found.")
                sdev.reset_input_buffer()
                newalert = [datetime.strftime(datetime.now(), '%c'), "Alert received."]
                alerts.append(newalert)

                # # The below code attempts to read data from serial line
                # # to fill in alert.
                # print("Incoming Data found.")
                # # Remove the trailing \r\n characters
                # sensVal = sdev.readline()[:-2]
                # print("Type: " + str(type(sensVal)))
                #
                # # Create a new alert
                # newalert = [datetime.strftime(datetime.now(), '%c'), sensVal]
                # print(newalert)
                # # Add new alert to the list
                # alerts.append(newalert)


                # Wait a second before continueing
                time.sleep(1)
        # When stopping, close the serial devices
        sdev.close()


# Create a new HTTP Server Instance
httpd = make_server(HOST, PORT, simple_app)

print "Serving on port %s:%s" % (HOST, str(PORT))

# Start the Application up
try:
    p = SerialThread()
    p.start()
    httpd.serve_forever()
except KeyboardInterrupt:
    p.stop()
    httpd.shutdown()

