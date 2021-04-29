/**
 * Module for RTC Peer Connection of the block-server.
 * @author [lusm554]{@link https://github.com/lusm554}
 * @requires RTCPeerConnection
 * @requires RTCSessionDescription
 */

const EventEmitter = require('events')
const { RTCPeerConnection, RTCSessionDescription } = require('wrtc')

class PeerConnection extends EventEmitter {
  constructor(offer, connection) {
    super()
    this.connection = connection 
    this.offer = offer
    
    this.connection.on('message', ({ utf8Data: msg }) => {
      msg = JSON.parse(msg)
      if (msg['new-ice-candidate']) return this.#ice_handler(JSON.parse(msg['new-ice-candidate']), connection);
    })
  }

  /**
   * Create peer connection, set remote desc and send answer client.
   * @returns {PeerConnection}
   */
  set_offer() {
    const conf = {
      'iceServers': [{'urls': 'stun:stun.l.google.com:19302'}]
    }

    this.peerConnection = new RTCPeerConnection(conf)
    this.#set_peerConnection_events(this.peerConnection)
    this.peerConnection.setRemoteDescription(new RTCSessionDescription(this.offer))
    this.peerConnection.createAnswer()
      .then(answer => this.peerConnection.setLocalDescription(answer))
      .then(() => this.connection.sendUTF(JSON.stringify({ offer: this.peerConnection.currentLocalDescription })))
    return this
  }

  /**
   * Add ice candidate and send response status.
   * @param {Object} ice - WebRTC candidate
   * @param {Object} connection - res object
   */
  #ice_handler(ice, connection) {
    this.peerConnection.addIceCandidate(ice)
      .catch(e => this.emit('error', e))
    connection.sendUTF(JSON.stringify({ status: 200 }))
  }

  /**
   * Add event handlers on peerConnection.
   * @param {Object} c - peer connection
   */
  #set_peerConnection_events(c) {
    c.addEventListener('datachannel', (e) => this.#data_channel_handler(e))
    c.addEventListener('iceconnectionstatechange', () =>  console.log('[peerConnection]', 'iceConnectionStateChange:', this.peerConnection.iceConnectionState))
    c.addEventListener('signalingstatechange', () => console.log('[peerConnection]', 'signalingStateChange:', this.peerConnection.signalingState))  
  }

  /**
   * Emit event with data and set listeners on receiveChannel.
   * @param {Object} e - listener event object
   */
  #data_channel_handler(e) {
    // Channel from client
    const receiveChannel = e.channel
    receiveChannel.addEventListener('message', (e) => {
      const msg = e.data
      if (typeof msg === 'object') {  
        return this.emit('buffer_data', msg)
      }
      return this.emit('message', msg)
    })
  
    const onReceiveChannelStateChange = ({ type }) => console.log(`[receiveChannel] ${type}`)
    receiveChannel.addEventListener('open', onReceiveChannelStateChange)
    receiveChannel.addEventListener('close', onReceiveChannelStateChange)
    receiveChannel.addEventListener('error', onReceiveChannelStateChange)
  }
}

module.exports = PeerConnection