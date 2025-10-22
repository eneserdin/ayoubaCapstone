from socket import *
import RPi.GPIO as GPIO
import ADC0834
from time import sleep

# GPIO setup
GPIO.setmode(GPIO.BCM)
ADC0834.setup()
GPIO.setup(20, GPIO.OUT)

serverName = '10.252.251.1'
serverPort = 12000

try:
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.settimeout(5.0)
    
    print("Client started. Press Ctrl+C to stop.")
    
    while True:
            # Read light sensor
            lightVal = ADC0834.getResult(0)
            message = bytes(str(lightVal), 'utf-8')
            
            # Send to server
            clientSocket.sendto(message, (serverName, serverPort))
            print(f"Sent light value: {lightVal}")
            
            # Wait for server response
            response, serverAddress = clientSocket.recvfrom(2048)
            
            # Control LED based on response
            if response == b'on':
                GPIO.output(20, True)
                print(f"Room too dark! (Value: {lightVal}) Firing up the Red LED")
            elif response == b'off':
                GPIO.output(20, False)
                print(f"Enough light! (Value: {lightVal}) Red LED off!!!")
                

            sleep(3)

except KeyboardInterrupt:
    print("\nClient shutting down gracefully...")


# Cleanup
clientSocket.close()
GPIO.cleanup()
print("GPIO cleaned up and socket closed")