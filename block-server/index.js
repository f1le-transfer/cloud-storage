/**
 * Main file of the block-server.
 * @author [lusm554]{@link https://github.com/lusm554}
 * @requires fs
 * @requires http
 * @requires websocket
 * @requires PeerConnection
 */

const { server: WebSocketServer } = require('websocket')
const http = require('http')
const fs = require('fs')
const path = require('path')
const PeerConnection = require('./RTCConnection')
const { worker, parentPort } = require('worker_threads') // unused
const { Queue } = require('./queue') // unused

const httpServer = http.createServer((req, res) => { res.statusCode = 404; res.end('Not found') })

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
const WORK_DIR = path.join(process.env.VAR_DATA || process.env.PWD, 'files')

/**
 * Size of the header in bytes
 * @type {number}
 */
const HEADER_LEN = 200

/**
 * Peer connection.
 * @type {class PeerConnection}
 */
let peerConnection;

/**
 * TODO: Rewrite code with non-blocking callbacks, with flexible header
 */

/**
 * Log data about socket to the console.
 * @param {*} data
 */
const log = (...data) => console.log('[WS]', ...data)

fs.promises.access(WORK_DIR)
  .catch(() => fs.promises.mkdir(WORK_DIR).catch(console.error))
  .finally(() => httpServer.listen(5050, () => console.log('Server run on 5050')))

/**
 * Receive messages from client.
 */
ws_server.on('request', (req) => {
  const connection = req.accept()
  log('Connected', req.origin)

  connection.on('message', msg_handler.bind(undefined, connection))
  connection.on('close', (code, desc) => log(`Closed ${req.origin} code:`, code, desc))
})

/**
 * Handle message.
 * @param {Object} connection - res object
 * @param {String} msg - data in utf-8
 * @returns {void}
 */
function msg_handler(connection, { utf8Data: msg }) {
  msg = JSON.parse(msg)
  if (msg.getListAvailableFiles) {
    return sendFileInformation(connection)
  }

  if (msg.offer && msg.remoteConn) {
    log('Offer received')
    peerConnection = new PeerConnection(connection).set_offer(JSON.parse(msg.offer))
    peerConnection.on('error', console.error)
    peerConnection.on('buffer_data', (data) => writeData(data))
    peerConnection.on('message', (msg) => console.log('[DATA CHANNEL]', msg))
    peerConnection.on('transferFile', transferFile)
  }
}

function transferFile(file) {
  try {
    console.log('[FILE REQUEST]', file)
    const parse = path.parse(file.name)
    fs.promises.readdir(path.join(parse.dir, parse.name))
      .then(chunks => {
        peerConnection.dataChannel.send(JSON.stringify({ len: chunks.length+1 }))
        return chunks
      })
      .then(chunks => {
        chunks.forEach(chunk_name => {
          fs.createReadStream(path.join(parse.dir, parse.name, chunk_name)).on('data', data_chunk => {
            peerConnection.dataChannel.send(data_chunk)
          })
        })
      })  
  } catch (error) {
    console.log(error)  
  }
}

// TODO: REWRITE ASYNC FUNCTION
function sendFileInformation(connection) {
  // function allFiles(dirPath, arrayOfFiles=[]) {
  //   let files = fs.readdirSync(dirPath)
  //   files.forEach(file => {
  //     if (fs.statSync(dirPath + "/" + file).isDirectory()) {
  //       allFiles(dirPath + "/" + file, arrayOfFiles)
  //     } else {
  //       arrayOfFiles.push(path.join(dirPath + '.' + file.split('.')[1]))
  //     }
  //   })
  //   return arrayOfFiles
  // }

  async function allFiles(dirPath, arrayOfFiles=[]) {
    let files = await fs.promises.readdir(dirPath)
    for (let file of files) {
      if (fs.statSync(path.join(dirPath, file)).isDirectory()) {
        await allFiles(path.join(dirPath, file), arrayOfFiles)
      } else {
        arrayOfFiles.push(path.join(dirPath + '.' + file.split('.')[1]))
      }
    }
    return arrayOfFiles
  }

  allFiles(WORK_DIR).then(files => {
    connection.sendUTF(JSON.stringify({ listAvailableFiles: Array.from(new Set(files)) }))
  })
  .catch(console.error)
}

/**
 * Create dir for clients files and write stream.
 * Create dir by file name and write in this dir file chunks.
 * @param {String} file - name of the file
 */
function createWriteStream(file) {
  try {
    // Create work directory if not exist
    let dir = file.dir ? path.join(WORK_DIR, file.dir, file.name) : WORK_DIR
    const file_path = path.join(WORK_DIR, file.dir || '', file.name, path.normalize(`${file.chunk}_${file.version || 1}${path.extname(file.full_name)}.chunk`))
    return fs.promises.mkdir(dir, { recursive: true })
      .then((isNotExist) => isNotExist && console.log('[FS]', `Dir ${dir} created.`))
      .then(() => fs.createWriteStream(file_path))
      .catch(console.error)
  } catch (error) {
    return Promise.reject(error)
  }
}

/**
 * Write chunk to file.
 * @param {ArrayBuffer} buffer - chunk of data
 */
function writeData(buffer) {
  const data_Uint8Array = new Uint8Array(buffer)

  const header = parse_header(data_Uint8Array)
  console.log('[HEADER]', header)

  createWriteStream(header)
    .then(writeStream => writeStream.write(data_Uint8Array.slice(HEADER_LEN), 'base64', (e) => e && console.log('[ERROR]', 'Error while writing data', e)))
    .catch(console.error)
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
