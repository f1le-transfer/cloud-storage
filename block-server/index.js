const { RTCPeerConnection, RTCSessionDescription } = require('wrtc')
const { server: WebSocketServer } = require('websocket')
const http = require('http')
const fs = require('fs')
const path = require('path')
const { worker, parentPort } = require('worker_threads')

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

const WORK_DIR = 'files'
const HEADER_LEN = 100
let peerConnection;
let writeStream;

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
        let data;
        try {
          data = JSON.parse(msg)
        } catch (error) {
          return console.error('[ERROR] prase json string from client.')
        }
        
        // If msg is info of the file
        if (data.name && data.dir) {
          return createWriteStream(data)
        }

        console.log('[receiveChannel MSG]', data)
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

function createWriteStream(file) {
  console.log('[receiveChannel MSG]', file)

  // Create work directory if not exist
  let dir = file.dir ? path.join(WORK_DIR, file.dir) : WORK_DIR
  fs.mkdirSync(dir, { recursive: true }, console.error)
  console.log('[FS]', `Dir ${path.join(file.dir, WORK_DIR)} created`)

  writeStream = fs.createWriteStream(file.dir ? path.join(WORK_DIR, file.dir, path.normalize(file.name)) : path.join(WORK_DIR, path.normalize(file.name)))
}

function writeData(buffer) {
  const data_Uint8Array = new Uint8Array(buffer)

  const header = parse_header(data_Uint8Array)
  console.log('[HEADER]', header)

  writeStream.write(data_Uint8Array.slice(HEADER_LEN), 'base64')
}

/**
 * Take header path from buffer.
 * @param {BufferArray|Uint8Array} buf – header from buffer
 * @returns {String}
 */
function parse_header(buf) {
  /**
   * Some methods for parse string from buffer.
   * – new TextDecoder("utf-8").decode(Uint8Array)
   * – String.fromCharCode.apply(null, Uint8Array)
   */
  const buf_header = new Uint8Array(buf).slice(0, HEADER_LEN)
  /**
   * In order to parse json from header
   * we need filter zeros from char numbers.
   */
  const char_arr = buf_header.slice(0, buf_header.indexOf(0))
  try {
    return JSON.parse(String.fromCharCode.apply(null, char_arr))
  } catch (error) {
    return console.error('[ERROR] Error while parse header from file chunk.')
  }
}