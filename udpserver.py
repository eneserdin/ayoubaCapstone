from socket import *
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("The server is ready to receive")

on= bytes("on", 'utf-8')
off = bytes("off", 'utf-8')
while 1:
    message, clientAddress = serverSocket.recvfrom(2048)
    lightVal = int(message.decode("utf-8"))
    print (lightVal)
    if lightVal<= 180:
       serverSocket.sendto(on, clientAddress)
    else:
        serverSocket.sendto(off, clientAddress)
    
    
    
    
    #print(modifiedMessage)
    #serverSocket.sendto(modifiedMessage, clientAddress)