#!/usr/bin/python
# Import the libraries to use time delays, send os commands and access GPIO pins
import RPi.GPIO as GPIO
from time import sleep
import os

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)  # Turn off warnings output
GPIO.setup(11, GPIO.OUT) # Set pin #11 (GPIO17) to output
GPIO.output(11,True)
GPIO.setup(13, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  # Set pin #13 (GPIO27) to input
GPIO.setup(12,GPIO.OUT)  # LED
GPIO.output(12,True)

while True:
    buttonIn = GPIO.input(13)

    if buttonIn == True:
        print('Shutdown button was push. System shutdown now!')
        sleep(1)
        GPIO.cleanup()
        #os.system("sudo reboot")
        os.system("sudo shutdown -h now")
        break
    sleep(1)
