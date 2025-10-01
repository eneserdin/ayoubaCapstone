#!/usr/bin/env python3

import RPi.GPIO as GPIO
import ADC0834
from time import sleep

#GPIO.cleanup()

on = True
off = False

GPIO.setmode(GPIO.BCM)
ADC0834.setup()
GPIO.setup(20, GPIO.OUT)
try:
    while True:
        lightVal=ADC0834.getResult(0)
        print("Light Value: ", lightVal)
        if lightVal <= 50:
            GPIO.output(20, on)
            print("Room too dark! Firing up the Red LED")
        else:
            GPIO.output(20, off)
            print("Enought light! Red LED off!!!")
        sleep(3)

except KeyboardInterrupt:
    sleep(.1)
    GPIO.cleanup()
    print("GPIO Good to Go!!!")