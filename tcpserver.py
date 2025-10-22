from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready to receive')


on = bytes("on", 'utf-8')
off = bytes("off", 'utf-8')

try:
    while True:
        connectionSocket, addr = serverSocket.accept()
        print(f"Connection established with {addr}")
        
        # Receive light value from client
        message = connectionSocket.recv(1024)
        lightVal = int(message.decode('utf-8'))
        print(f"Received light value: {lightVal}")
            
        # Determine response based on light value
        if lightVal <= 180:
            connectionSocket.send(on)
            print(f"Sent: ON (value: {lightVal} <= 180)")
        else:
             connectionSocket.send(off)
             print(f"Sent: OFF (value: {lightVal} > 180)")
                
        

except KeyboardInterrupt:
    print("\nServer shutting down...")
    
serverSocket.close()