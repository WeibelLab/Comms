from ReliableCommunication import Client
import time


def requestResponse(message):
    ''' Client 1's callback '''
    time.sleep(1)
    if message != "quit":
        res = str(input("CL1, What do you have to say? > "))
        myClient1.send(res)
        if res == "quit":
            myClient1.close()

def echo(message):
    ''' Client 2's callback '''
    print("CL2: {}".format(message))
    if message == "quit":
        myClient2.close()

def onclose(client):
    print("Connection to {}:{} closed".format(client.address, client.port))

# Instantiate objects
myClient1 = Client(address="127.0.0.1", port=12345, messageDataType="string", autoReconnect=False)
myClient2 = Client(address="127.0.0.1", port=12345, messageDataType="string")

# Setup Callbacks
myClient1.add_onmessage_callback(requestResponse)
myClient2.add_onmessage_callback(echo)
myClient1.add_onclose_callback(onclose)
myClient2.add_onclose_callback(onclose)

myClient1.add_onconnect_callback(requestResponse) # to get the ball rolling

# Start server and clients
myClient1.connect()
myClient2.connect()