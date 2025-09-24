from socket import *
serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('The server is ready to receive')
while 1:
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024)
    capitalizedSentence = sentence.upper();
    print(capitalizedSentence);
    mystr = capitalizedSentence.decode("utf-8")
    print(mystr);
    commands = mystr.split(":")
    print(commands);
    print("You want " + commands[0] + " to be:",int(commands[1]))
   
    #
    # insert your pi function
    #
    connectionSocket.send(capitalizedSentence)
    connectionSocket.close()