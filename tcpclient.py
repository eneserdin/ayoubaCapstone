from socket import *
import RPi.GPIO as GPIO
import ADC0834
from time import sleep

# GPIO setup
GPIO.setmode(GPIO.BCM)
ADC0834.setup()
GPIO.setup(20, GPIO.OUT)

serverName = '10.252.251.1'  #Change this
serverPort = 12000

try:
    print("TCP Client started. Press Ctrl+C to stop.")
    
    while True:
        # Create new connection for each reading
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
            
        # Read light sensor and send to server
        lightVal = ADC0834.getResult(0)
        message = bytes(str(lightVal), 'utf-8')
        clientSocket.send(message)
        print(f"Sent light value: {lightVal}")
            
        # Receive response from server
        response = clientSocket.recv(1024)
            
        # Control LED based on response
        if response == b'on':
            GPIO.output(20, True)
            print(f"Room too dark! (Value: {lightVal}) Firing up the Red LED")
        else:
            GPIO.output(20, False)
            print(f"Enough light! (Value: {lightVal}) Red LED off!!!")
                
            
        sleep(3)

except KeyboardInterrupt:
    print("\nClient shutting down gracefully...")

GPIO.cleanup()
print("GPIO cleaned up")
clientSocket.close()