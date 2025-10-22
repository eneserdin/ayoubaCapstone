from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("The server is ready to receive")


on = bytes("on", 'utf-8')
off = bytes("off", 'utf-8')

try:
    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        try:
            lightVal = int(message.decode("utf-8"))
            print(f"Received light value: {lightVal} from {clientAddress}")
            
            if lightVal <= 180:
                serverSocket.sendto(on, clientAddress)
                print(f"Sent: ON (value: {lightVal} <= 180)")
            else:
                serverSocket.sendto(off, clientAddress)
                print(f"Sent: OFF (value: {lightVal} > 180)")
                
        except ValueError:
            print(f"Error: Received non-numeric value: {message}")
            # Optionally send an error response back to client
            
except KeyboardInterrupt:
    print("\nServer shutting down...")
finally:
    serverSocket.close()
    print("Server socket closed")