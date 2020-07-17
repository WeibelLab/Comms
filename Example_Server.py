from ReliableCommunication import Server

myServer = Server(address="0.0.0.0", port=12345, messageDataType="string")

def broadcast(message):
    ''' server's callback '''
    myServer.broadcast(message)
    print("<server broadcast message: '{}'>".format(message))

def onConnection(client):
    print("{}:{} Connected".format(client.address, client.port))

def onDisconnection(client):
    print("{}:{} Diconnected".format(client.address, client.port))


myServer.add_onmessage_callback(broadcast)
myServer.add_onconnect_callback(onConnection)
myServer.add_onclose_callback(onDisconnection)
myServer.start()

input("\tPRESS ANY KEY TO EXIT\n")
myServer.stop()