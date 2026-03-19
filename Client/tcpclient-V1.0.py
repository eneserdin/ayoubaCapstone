from socket import *
import RPi.GPIO as GPIO
import ADC0834
from time import sleep

# GPIO setup
GPIO.setmode(GPIO.BCM)
ADC0834.setup()
GPIO.setup(20, GPIO.OUT)

serverName = '10.8.0.5'  
serverPort = 12000

try:
    print("TCP Client started. Press Ctrl+C to stop.")
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    
    while True:
        # Read light sensor and send to server
        lightVal = ADC0834.getResult(0)
        message = bytes(str(lightVal), 'utf-8')
        clientSocket.send(message)
        print(f"Sent light value: {lightVal}")
            
        # Receive response from server
        response = clientSocket.recv(1024)
            
        # Control LED based on response
        if response == b'on':
            GPIO.output(22, True)
            print(f"Room too dark! (Value: {lightVal}) Firing up the Red LED")
        else:
            GPIO.output(22, False)
            print(f"Enough light! (Value: {lightVal}) Red LED off!!!")
                
            
        sleep(3)

except KeyboardInterrupt:
    print("\nClient shutting down gracefully...")

GPIO.cleanup()
print("GPIO cleaned up")
clientSocket.close()