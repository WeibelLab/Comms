const express = require('express');
const fs = require('fs');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;
const urlencodedParser = bodyParser.urlencoded({ extended: false })  

let rooms = {
    // "blue-dog": {
    //     "key": "inkoay",
    //     "devices": {
    //         "asdf": {
    //             "type": "server",
    //             "ip": "192.168.1.100",
    //             "port": 4000
    //         }
    //     }
    // }
}

app.get('/test', (req, res, next) => {
    res.send(`<html>  
    <body>  
    <form id="f" action="/join" method="POST">  
    ID: <input type="text" name="id"><br>
    Passkey: <input type="text" name="key"><br>
    Room: <input type="text" name="room"><br>
    Port: <input type="text" name="port"><br>
    Type: <select name="type" form="f">
        <option value="server">I am a Server</option>
        <option value="client">I am a Client</option>
    </select><br>
    <input type="submit" value="Submit">  
    </form>  
    </body>  
    </html>`)
})

app.get('/rooms', (req, res, next) => {
    console.log("[GET][/rooms]");
    res.end(JSON.stringify(Object.keys(rooms)));
});

app.get('/rooms/:name', (req, res, next) => {
    console.log("[GET][/room]");
    if (req.params.name in rooms) {
        res.send("<pre><code>"+JSON.stringify(rooms[req.params.name].devices, null, 4)+"</code></pre>");
    }
    else {
        res.redirect("/rooms");
    }
})

app.post('/join', urlencodedParser, (req, res, next) => {
    console.log("[POST][/join]");
    
    let data = { 
        id: req.body.id,
        key: req.body.key,
        room: req.body.room,
        type: req.body.type.toLowerCase(),
        ip: req.headers['x-forwarded-for'] || req.socket.remoteAddress,
        port: parseInt(req.body.port)
    };
    if (!data.id || !data.key || !data.room || !data.type) {
        res.status(400).end("Must provide an id, key, room, and type <br>Server was given<br>"+JSON.stringify(data, null, 4));
    }
    
    // Add Device to existing Room
    if (data.room in rooms) {
        let room = rooms[data.room];
        // Check for correct passkey
        if (data.key === room.key) {
            // Add device to list of room's devices
            if (data.type === "server") {
                updateServer(data);
                res.end(JSON.stringify(simplifyDevices(rooms[data.room]))); // give new server a list of clients
            }
            else if (data.type === "client") {
                rooms[data.room].devices[data.id] = data;
                res.end(JSON.stringify(getServerInfo(room))); // give client the server info
            }
            else {
                res.status(400).end("Invalid device type. Must be 'server' or 'client'");
            }
        }
        else {
            res.status(403).end("Invalid key");
        }
    }
    // Create new room
    else if (data.type === "server") {
        console.log("Creating new room", data.room);
        rooms[data.room] = {
            "key": data.key,
            "devices": {}
        }
        rooms[data.room].devices[data.id] = data;
        res.end("");
    }
    else {
        res.status(404).end("Could not find requested room")
    }

});

/**
 * Updates the server for a room based on a new device's data
 * @param {object} res the response object
 * @param {object} data posted data with 'type', 'id', 'key', 'room', and 'ip'
 */
function updateServer(data) {
    // Update Server (only 1 server per room)
    let serverId = getServerIdFromRoom(rooms[data.room]);
    delete rooms[data.room].devices[serverId]
    rooms[data.room].devices[data.id] = data;
}

/**
 * Gets the server id from a room
 * @param {object} room The room to search through for the server
 * @returns the id of the server
 */
function getServerIdFromRoom(room) {
    for (let d in room.devices) {
        if (room.devices[d].type === "server") {
            return d;
        }
    }
}

/**
 * Gets the IP address of the server in a room
 * @param {Object} room The room to search
 * @returns server's ip and port
 */
function getServerInfo(room) {
    let id = getServerIdFromRoom(room);
    return {
        ip: room.devices[id].ip,
        port: room.devices[id].port
    }
}

function simplifyDevices(room) {
    let devices = []
    for (let d in room.devices) {
        devices.push({
            ip: room.devices[d].ip,
            port: room.devices[d].port,
            type: room.devices[d].type
        })
    }
    return devices;
}



// Start Server
app.listen(PORT, () => {
    console.log("Listening on", PORT);
});

// module.exports = app; // TODO: Make into a module