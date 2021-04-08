const { RTCPeerConnection, RTCSessionDescription } = require('wrtc')
const { server: WebSocketServer } = require('websocket')
const http = require('http');
const fs = require('fs')
const path = require('path')

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

const work_dir = 'files'
let peerConnection;
let writeStream;

// TODO:
// 1. Close write stream after file end
// 2. Work with file system

function msg_handler(origin, connection, { utf8Data: msg }) {
    msg = JSON.parse(msg)
    if (msg.offer) {
        log('Offer received')
        return offer_handler(JSON.parse(msg.offer), connection)
    }
    if (msg['new-ice-candidate']) {
        log('Candidate received')
        return ice_handler(JSON.parse(msg['new-ice-candidate']), connection)
    }
    log(msg)
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
        // Get data channel from client
        const receiveChannel = event.channel
        receiveChannel.addEventListener('message', (e) => {
            const msg = e.data
            if (typeof msg === 'string') {
                return createWriteStream(msg)
            }

            if (typeof msg == 'object') {
                console.log('[receiveChannel MSG]', 'length', msg.byteLength)
                return writeData(msg)
            }
        })

        const onReceiveChannelStateChange = ({ type }) => console.log(`[receiveChannel] ${type}`)
        receiveChannel.addEventListener('open', onReceiveChannelStateChange)
        receiveChannel.addEventListener('close', onReceiveChannelStateChange)
        receiveChannel.addEventListener('error', onReceiveChannelStateChange)
    })
    peerConnection.addEventListener('iceconnectionstatechange', () =>  console.log('[peerConnection]', 'iceConnectionStateChange:', peerConnection.iceConnectionState))
    peerConnection.addEventListener('signalingstatechange', () => console.log('[peerConnection]', 'signalingStateChange:', peerConnection.signalingState))
}

function createWriteStream(msg) {
    let file;
    try {
        file = JSON.parse(msg)
    } catch (error) {
        return console.error('[ERROR] prase json string from client')
    }
    console.log('[receiveChannel MSG]', file)

    // Create work directory if not exist
    fs.mkdirSync(work_dir, { recursive: true }, console.error)

    writeStream = fs.createWriteStream(path.join(work_dir, path.normalize(file.name)))
}

function writeData(buffer) {
    const data_Uint8Array = new Uint8Array(buffer)
    writeStream.write(data_Uint8Array, 'base64')
}