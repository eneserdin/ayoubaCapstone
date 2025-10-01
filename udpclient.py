from socket import *
import RPi.GPIO as GPIO
import ADC0834
from time import sleep


GPIO.setmode(GPIO.BCM)
ADC0834.setup()
GPIO.setup(20, GPIO.OUT)

serverName = '10.252.251.1'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
while True:
    lightVal=ADC0834.getResult(0)
    message = bytes(str(lightVal), 'utf-8') # raw_input in python 2
    clientSocket.sendto(message,(serverName, serverPort))
    Message, serverAddress = clientSocket.recvfrom(2048)
    if Message == b'on':
        GPIO.output(20, True)
        print("Room too dark! Firing up the Red LED")
    else:
        GPIO.output(20, False)
        print("Enought light! Red LED off!!!")
        
    sleep(3)

clientSocket.close()
GPIO.cleanup()