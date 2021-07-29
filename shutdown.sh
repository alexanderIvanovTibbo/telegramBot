#!/usr/bin/python
# Import the libraries to use time delays, send os commands and access GPIO pins
import RPi.GPIO as GPIO
from time import sleep
import os
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)  # Turn off warnings output
GPIO.setup(11, GPIO.OUT) # Set pin #11 (GPIO17) to button output
GPIO.setup(18, GPIO.OUT) # Set pin #18 (GPIO17) to LED output
GPIO.output(11,True)
GPIO.setup(12, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  # Set pin #12 (GPIO18) to input

while True:
    buttonIn = GPIO.input(12)

    if buttonIn == True:
        print('Shutdown button was push. System shutdown now!')
        sleep(1)
        GPIO.cleanup()
#        os.system("sudo reboot")
        os.system("sudo shutdown -h now")
        break
    sleep(1)
