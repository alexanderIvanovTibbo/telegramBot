#!/usr/bin/python
# Import the libraries to use time delays, send os commands and access GPIO pins
import RPi.GPIO as GPIO
from time import sleep
import os
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)  # Turn off warnings output
GPIO.setup(22, GPIO.OUT) # Set pin #22 to RELAY output
GPIO.output(22,True)
GPIO.setup(21, GPIO.OUT) # Set pin #21 to MOSFET output
GPIO.setup(19, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  # Set pin #19 to RELAY input
flagStatus = None
while True:
    buttonIn = GPIO.input(19)
    print(buttonIn)
    print(flagStatus)
    if buttonIn:
        if flagStatus is None:
           print('Power ON')
           flagStatus = False
    else:
        if not flagStatus:
           print('Power OFF')
           flagStatus = True
    sleep(1)
#        GPIO.cleanup(21)
#    sleep(1)
