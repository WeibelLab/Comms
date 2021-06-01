import socket
from datetime import datetime
import socket, time, threading, time, sys, json

class Server:
    def __init__(self, address, port, messageDataType="json", byteOrder='little', sendMostRecent=False):
        self.port = port
        self.address = address
        self.sock = None
        self.clients = []
        self.STOP = False
        self.dataToSend = None
        self.sendMostRecent = sendMostRecent
        self.lock = threading.Lock()
        self.messageDataType = messageDataType
        self.byteOrder = byteOrder
        self.__onmessage_callbacks__ = []
        self.thread = threading.Thread(target=self.__receive_loop__, name="Server {} receive_loop".format(self.port))

        print("[Server "+str(self.port)+"] Initialized. (Still needs to be started)")

    def start(self):
        '''
        Starts the server - begins accepting clients
        will create threads for each client that connects.
        Allows for Server.MAX_CLIENTS number of clients to connect
        '''
        self.thread.start()
        print("[Server "+str(self.port)+"] Started.")

    def __receive_loop__(self):
        ''' Constantly listen and accept clients '''
        print("[Server {}] Open for new connections".format(self.port))

        # Constantly look for a connection
        while not self.STOP:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                self.sock.bind((self.address, self.port))
            except:
                print("[Server "+str(self.port)+"] Port already in use")
                self.sock.close()
                self.sock = None
                time.sleep(Server.PORT_IN_USE_TIMEOUT)
                continue

            while not self.STOP:

                # Accept incoming connections
                self.sock.settimeout(3)
                try:
                    # Get Message Header
                    datalen_bytes, addr = self.sock.recvfrom(4)
                    datalen = int.from_bytes(datalen_bytes, self.byteOrder)
                    data = self.sock.recv(datalen) # and message
                    
                    # Parse Data into a message based self.messageType
                    msg = data
                    if self.messageDataType == "json":
                        msg = Client.parseJson(data)
                    elif self.messageDataType == "string":
                        msg = msg.decode("utf-8")

                    # Callback
                    threading.Thread(target=self.__onmessage_caller__, args=(msg,), name="Client {}:{} onmessage_callbacks".format(self.address, self.port)).start()

                    # Check if new client
                    if addr in self.clients:
                        self.clients.append(Client(addr[0], addr[1], controlledByServer=True, connection=None, alsoListen=False, messageDataType=self.messageDataType, byteOrder=self.byteOrder, sendMostRecent=self.sendMostRecent))
                except socket.timeout:
                    continue
                except ConnectionResetError:
                    continue
                except ConnectionAbortedError:
                    continue
                except:
                    print("[Client {}:{}] Exception in read loop \n\t{}".format(self.address, self.port, sys.exc_info()))
                    self.stop()
                    continue

        if (self.sock):
            self.sock.close()
            print("[Server {}] Socket Closed".format(self.port))


    ''' 
    CALLBACK METHODS
    '''

    def __onmessage_caller__(self, message):
        ''' Calls all of the subscribed listeners whenever a client gets a message '''
        for callback in self.__onmessage_callbacks__:
            callback(message)

    def add_onmessage_callback(self, func):
        '''
        Adds passed function to list of callback functions.
        All functions will be called when server receives a message from any of the clients
        function will be called in the order they are added
        @param func the function to add. eg: myServer.add_onmessage_callback(dosomething) 
        '''
        self.__onmessage_callbacks__.append(func)

    def remove_onmessage_callback(self, func=None, index=0):
        '''
        Removes passed function OR index from list of callbacks
        @param func (optional) the function to add. If None, will use 'index'
        @param index the index of the function to remove. 'func' must be None.
        '''
        Server.__remove_func_from_list__(self.__onmessage_callbacks__, func, index)

    def __remove_client__(self, client):
        ''' removes client from server's list of clients '''
        self.clients.remove(client)

    @staticmethod
    def __remove_func_from_list__(listToModify, func=None, index=0):
        ''' logic to remove either a function or index from a list '''
        if func is not None:
            if func in listToModify:
                listToModify.remove(func)
                return True
            else:
                return False
        
        if 0 < index < len(listToModify):
            listToModify.pop(index)
            return True
        else:
            return False

    '''
    SENDING METHODS
    '''
    def sendAll(self, data):
        self.broadcast(data)

    def broadcast(self, data):
        '''
        Send a message to all clients connected to the server
        @param data the message to send - either json, string, or binary (can be different from what the server parses)
        '''
        for client in self.clients:
            threading.Thread(target=client.send, args=(data,), name="Client {}:{} send".format(client.address, client.port)).start()

    def sendTo(self, data, server_client=0):
        '''
        Send a message to a particular client
        @param data to message to send - either json, string, or binary
        @param server_client can be client index or the client object you wish to send to
        '''
        if type(server_client) is type(0):
            if server_client < len(self.clients):
                self.clients[server_client].send(data)
                return
            else:
                raise IndexError("Passed index {} but only {} clients exist".format(server_client, len(self.clients)))

        if type(server_client) is type(Client):
            server_client.send(data)

    def __del__(self):
        self.stop()

    def stop(self):
        '''
        Stops the server. Disconnects clients. Ends all threads.
        Use this to cleanly close everything.
        '''
        if not self.STOP:
            self.STOP = True
            for client in self.clients:
                client.conn.shutdown(1)
                client.close()
        
            print("[Server {}] Stopping... ({} second timeout)".format(self.port, Server.PORT_IN_USE_TIMEOUT))



    






class Client:
    def __init__(self, address, port, controlledByServer=False, connection=None, alsoListen=False, messageDataType="json", byteOrder='little', sendMostRecent=False):
        # connection and message passing type
        self.address = address
        self.port = port
        self.conn = connection
        self.messageType = messageDataType
        self.byteOrder = byteOrder
        # state management
        self.STOP = False
        self.listener = None
        self.alsoListen = alsoListen
        # listeners
        self.onMessage = []
        # options
        self.autoReconnect = False
        self.__can_connect__ = False
        self.sendMostRecent = sendMostRecent
        if self.conn is None or controlledByServer is False:
            self.__can_connect__ = True
        else:
            self.listener = threading.Thread(target=self.__listen__, name="Client of {}:{} listener".format(self.address, self.port))


    '''
    CONTROL METHODS
    '''

    def connect(self):
        '''
        Starts connection with server. 
        '''
        if self.__can_connect__:
            self.STOP = False
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.conn.connect((self.address, self.port))
            if self.alsoListen:
                self.listener = threading.Thread(target=self.__listen__, name="Client of {}:{} listener".format(self.address, self.port))
                self.listener.start()
        else:
            raise Exception("Cannot establish client connection inside a server")
            
    def __listen__(self):
        ''' Constantly listens for messages, automatically parses as json or string, and starts callback threads '''
        while not self.STOP:
            if (self.conn):
                try:
                    # Get Message Header
                    self.conn.settimeout(3)
                    datalen = int.from_bytes(self.conn.recv(4), self.byteOrder)
                    data = self.conn.recv(datalen)
                    
                    # Parse Data into a message based self.messageType
                    msg = data
                    if self.messageType == "json":
                        msg = Client.parseJson(data)
                    elif self.messageType == "string":
                        msg = msg.decode("utf-8")

                    # Callback
                    threading.Thread(target=self.__onmessage_caller__, args=(msg,), name="Client {}:{} onmessage_callbacks".format(self.address, self.port)).start()
                except socket.timeout:
                    continue
                except ConnectionResetError:
                    continue
                except ConnectionAbortedError:
                    continue
                except:
                    print("[Client {}:{}] Exception in read loop \n\t{}".format(self.address, self.port, sys.exc_info()))
                    self.close()
                    continue
            else:
                self.close()
        
        # Close out
        self.conn.close()

    def send(self, message):
        ''' Sends a message '''
        # TODO: make this into a queue
        as_bytes = None
        as_string = None

        # Convert to bytes
        if type(message) is dict:
            as_string = json.dumps(message)
        elif type(message) is str:
            as_string = message
        elif type(message) is bytes:
            as_bytes = message
        else:
            raise TypeError("[UnreliableComms > send] message must by dict, str, or bytes type")
        if as_string is not None:
            as_bytes = as_string.encode("utf-8")

        # Add Header
        if (self.conn is not None and not self.STOP):
            # Get Message Length
            messageLength = (len(as_bytes)).to_bytes(4, byteorder=self.byteOrder, signed=False)

            # SEND
            try:
                self.conn.send(bytes(messageLength)) # 4 bytes with the size of the image
                self.conn.send(bytes(as_bytes)) # If throwing error, check if numpy array is converting to byte array. May need to call bytes(data.tobytes()) ERROR: only integer arrays with one element can be...
            except TypeError:
                tb = sys.exc_info()[2]
                print("[Client {}:{}] Exception sending data {}\n\t{} {}".format(self.address, self.port, sys.exc_info()[1], tb.tb_frame.f_code.co_filename, tb.tb_lineno))
            # except ConnectionAbortedError:
            #     self.close()
            # except ConnectionResetError:
            #     self.close()
            # except BrokenPipeError:
            #     self.close()
            # except OSError:
            #     self.close()
            except:
                self.close()
        
    def close(self):
        if not self.STOP:
            self.STOP = True

            # Autoreconnect
            if (self.autoReconnect):
                time.sleep(1)
                self.connect()

    ''' 
    CALLBACK METHODS
    '''

    def __onmessage_caller__(self, message):
        ''' Calls all of the subscribed listeners whenever a client gets a message '''
        for callback in self.onMessage:
            callback(message)

    def add_onmessage_callback(self, func):
        '''
        Adds passed function to list of callback functions.
        All functions will be called when client receives a message from the server
        function will be called in the order they are added
        @param func the function to add. eg: myClient.add_onmessage_callback(dosomething) 
        '''
        self.onMessage.append(func)
  
    def remove_onmessage_callback(self, func=None, index=0):
        '''
        Removes passed function OR index from list of callbacks
        @param func (optional) the function to add. If None, will use 'index'
        @param index the index of the function to remove. 'func' must be None.
        '''
        Client.__remove_func_from_list__(self.onMessage, func, index)

    '''
    HELPER
    '''

    def __eq__(self, o: object) -> bool:
        if type(o) is tuple:
            if o[0] == self.address and o[1] == self.port:
                return True
        else:
            return o==self
    
    @staticmethod
    def __remove_func_from_list__(listToModify, func=None, index=0):
        ''' logic to remove either a function or index from a list '''
        if func is not None:
            if func in listToModify:
                listToModify.remove(func)
                return True
            else:
                return False
        
        if 0 < index < len(listToModify):
            listToModify.pop(index)
            return True
        else:
            return False

    @staticmethod
    def parseJson(data):
        data = data.decode("utf-8")
        msg = json.loads(data)
        return msg