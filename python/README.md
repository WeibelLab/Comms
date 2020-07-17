# Python Comms
**Easy to use** multithreaded python server and client with support for json, strings, and binary message passing. Uses a UInt32 header to guarantee full messages are received.

Run both `Example_Server.py` and `Example_Clients.py` on the same computer to test and explore.

## ReliableCommunication.py
python file containing 2 classes
### Server
Can be used to create a multiclient, multithreaded server in just a few lines. The server will automatically allow new connections, has functions for broadcasting, and lets you subscribe to connection, disconnection, and message events.

#### Sample usage
see `Example_Server.py`
```python
from ReliableCommunication import Server

myServer = Server("0.0.0.0", 3000)
myServer.start()
```
That's all you need to get started. If you want to add additional specifications you can add some in the initialization
```python
Server(
    address="0.0.0.0",
    port=6000,
    messageDataType="json", #other options: "string" and "binary"
    byteOrder="little", #edianess
)
```

### Client
Can be used to create threaded TCP clients in just a few lines. Client has options to automatically reconnect. This class is also used by the Server class.

#### Sample Usage
see `Example_Clients.py` which creates 2 clients connecting to the same server.
```python
from ReliableCommunication import Client

myClient = Client("127.0.0.1", 6000)
myClient.connect()
```
That's all you need to get started. There are additional options you can specify when instantiating
```python
Client(
    address="127.0.0.1",
    port=6000,
    messageDataType="json" # also supports "string" and "binary",
    autoReconnect=True, # automatically reconnects to server if connection is severed for any reason
    byteOrder="little", # endianess
    
    # additionally, you can set these if you want to make your own custom server
    controlledByServer=False,
    connection=None
)
```



## Event Handling
3 events exist for both **Server** and **Client**
- **OnConnect**: 
    - Server: when *any* client connects to the server.Passes a reference to the Client object
    - Client: when client connects or reconnects to the server. No reference passed.
- **OnClose**:  
    - Server: when *any* client disconnects from the server. Passes a reference to the Client object that disconnected
    - Client: when client disconnects from server
- **OnMessage**: 
    - Server: when *any* client sends a message to the server. Currently does not provide a way for distinguishing between senders.
    - Client: when message is received from the server

To setup callbacks:
```python
myServer.add_onconnect_callback(myOnConnectFunction)
myServer.add_onclose_callback(myOnCloseFunction)
myServer.add_onmessage_callback(myOnMessageFunction)
```
where `myOnConnectFunction(clientObject)`, `myOnCloseFunction(clientObject)`, and `myOnMessageFunction(message)` are your custom functions for handling these events.