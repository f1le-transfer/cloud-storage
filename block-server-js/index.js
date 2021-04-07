const { RTCPeerConnection, RTCSessionDescription } = require('wrtc')
const { server: WebSocketServer } = require('websocket')
const http = require('http');

const httpServer = http.createServer((req, res) => { res.statusCode = 404; res.end('Not found') })
httpServer.listen(5050, () => console.log('Server run on 5050'))

ws_server = new WebSocketServer({
    httpServer,
    autoAcceptConnections: false
})

const log = (...data) => console.log('[WS]', ...data)
ws_server.on('request', (req) => {
    const connection = req.accept()
    log('Connected', req.origin)

    connection.on('message', msg_handler.bind(undefined, req.origin, connection))
    connection.on('close', close_handler.bind(undefined, req.origin))
})

let peerConnection;

function msg_handler(origin, connection, { utf8Data: msg }) {
    log('msg')
    msg = JSON.parse(msg)

    if (msg.offer) {
        offer_handler(JSON.parse(msg.offer), connection)
    }

    if (msg['new-ice-candidate']) {
        ice_handler(JSON.parse(msg['new-ice-candidate']), connection)
    }
}

async function offer_handler(offer, connection) {
    const configuration = {
        'iceServers': [{'urls': 'stun:stun.l.google.com:19302'}]
    }

    peerConnection = new RTCPeerConnection(configuration)
    set_peerConnection_events()
    peerConnection.setRemoteDescription(new RTCSessionDescription(offer))
    peerConnection.createAnswer()
        .then(answer => peerConnection.setLocalDescription(answer))
        .then(() => connection.sendUTF(JSON.stringify({ offer: peerConnection.currentLocalDescription })))
}

function ice_handler(ice, connection) {
    peerConnection.addIceCandidate(ice)
        .catch(console.error)
    connection.sendUTF(JSON.stringify({ status: 200 }))
}

function close_handler(origin, code, desc) {
    log(`Closed ${origin} code:`, code, desc)
}

function set_peerConnection_events() {
    peerConnection.addEventListener('datachannel', event => {
        const dataChannel = event.channel
        console.log('[DATA CHANNEL]', event.channel)

        dataChannel.addEventListener('message', (e) => {
            const msg = e.data
            console.log('[MSG]', msg)
        })
    
        dataChannel.addEventListener('open', console.log);
        dataChannel.addEventListener('close', console.log);
        dataChannel.addEventListener('error', console.error);
    });
}

