/**
 * Main file of the block-server.
 * @author [lusm554]{@link https://github.com/lusm554}
 * @requires fs
 * @requires http
 * @requires RTCPeerConnection, RTCSessionDescription
 * @requires websocket
 */

const { RTCPeerConnection, RTCSessionDescription } = require('wrtc')
const { server: WebSocketServer } = require('websocket')
const http = require('http')
const fs = require('fs')
const path = require('path')
const { worker, parentPort } = require('worker_threads')
const { Queue } = require('./queue')

const httpServer = http.createServer((req, res) => { res.statusCode = 404; res.end('Not found') })
httpServer.listen(5050, () => console.log('Server run on 5050'))

/**
 * Web socket server
 * @type {WebSocketServer}
 */
ws_server = new WebSocketServer({
  httpServer,
  autoAcceptConnections: false
})

/**
 * Directory for client files.
 * @type {string}
 */
const WORK_DIR = 'files'

/**
 * Size of the header in bytes
 * @type {number}
 */
const HEADER_LEN = 100

/**
 * Peer connection.
 * @type {object}
 */
let peerConnection;

/**
 * Writeable stream.
 * @type {object}
 */
let writeStream;

/**
 * TODO: Rewrite code with non-blocking callbacks
 */

/**
 * Log data about socket to the console.
 * @param {*} data
 */
const log = (...data) => console.log('[WS]', ...data)

/**
 * Receive messages from client.
 */
ws_server.on('request', (req) => {
  const connection = req.accept()
  log('Connected', req.origin)

  connection.on('message', msg_handler.bind(undefined, req.origin, connection))
  connection.on('close', close_handler.bind(undefined, req.origin))
})

/**
 * Handle message.
 * @param {String} origin - request host
 * @param {Object} connection - res object
 * @param {String} msg - data in utf-8
 * @returns {void}
 */
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

/**
 * Create peer connection, set remote desc and send asnwer to the client.
 * @param {Object} offer - WebRTC offer from client
 * @param {Object} connection - res object
 * @returns {void}
 */
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

/**
 * Add ice candidate and send response status.
 * @param {Object} ice - WebRTC candidate
 * @param {Object} connection - res object
 */
function ice_handler(ice, connection) {
  peerConnection.addIceCandidate(ice)
    .catch(console.error)
  connection.sendUTF(JSON.stringify({ status: 200 }))
}

/**
 * Call when websocket connection closed.
 * @param {String} origin - request host
 * @param {Number} code - close code
 * @param {String} desc - desc why connection closed
 */
function close_handler(origin, code, desc) {
  log(`Closed ${origin} code:`, code, desc)
}

/**
 * Add event handlers on peerConnection.
 */
function set_peerConnection_events() {
  peerConnection.addEventListener('datachannel', data_channel_handler)
  peerConnection.addEventListener('iceconnectionstatechange', () =>  console.log('[peerConnection]', 'iceConnectionStateChange:', peerConnection.iceConnectionState))
  peerConnection.addEventListener('signalingstatechange', () => console.log('[peerConnection]', 'signalingStateChange:', peerConnection.signalingState))
}

/**
 * Parse messages and set listeners on receiveChannel.
 * @param {Object} event - listener event object
 */
function data_channel_handler(event) {
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
}

/**
 * Create dir for clients files and write stream.
 * @param {String} file - name of the file
 */
function createWriteStream(file) {
  console.log('[receiveChannel MSG]', file)

  // Create work directory if not exist
  let dir = file.dir ? path.join(WORK_DIR, file.dir) : WORK_DIR
  fs.mkdirSync(dir, { recursive: true }, console.error)
  console.log('[FS]', `Dir ${path.join(file.dir, WORK_DIR)} created`)

  writeStream = fs.createWriteStream(file.dir ? path.join(WORK_DIR, file.dir, path.normalize(file.name)) : path.join(WORK_DIR, path.normalize(file.name)))
}

/**
 * Write chunk to file.
 * @param {ArrayBuffer} buffer - chunk of data
 */
function writeData(buffer) {
  const data_Uint8Array = new Uint8Array(buffer)

  const header = parse_header(data_Uint8Array)
  console.log('[HEADER]', header)

  writeStream.write(data_Uint8Array.slice(HEADER_LEN), 'base64', (e) => e && console.log('[ERROR]', 'Error while writing data', e))
}

/**
 * Take header path from buffer.
 * @param {ArrayBuffer|Uint8Array} buf – header from buffer
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