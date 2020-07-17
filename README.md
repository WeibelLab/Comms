# Comms
Easy to use Remote Communication classes

```
from ReliableCommunication import *

myServer = Comm(address="0.0.0.0", port=12345, isServer=True)
myServer.start()

# do stuff
myServer.broadcast(myjson)

# do more
myServer.broadcast(myjson)

# get stuff
function myFunc(jsondata):
    if jsondata["type"] == "annotation":
        # do something
    return

myServer.onDataReceivedCallbackFunctions_json.append(myFunction)
```