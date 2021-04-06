import json
import asyncio
import websockets
import uuid

from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCIceCandidate

host = '127.0.0.1'
port = 5050
# set of ...
pcs = set()
peerConnection = None

class clsprops:
	def __init__(self, data):
		self.__dict__ = data

async def offer_handler(msg, remote, ws):
    global peerConnection
    # Create peer connection

    config = {
        'iceServers': [clsprops({'urls': 'stun:stun.l.google.com:19302'})],
    }

    peerConnection = RTCPeerConnection(clsprops(config))
    pc_id = "[PeerConnection(%s)]" % uuid.uuid4()
    pcs.add(peerConnection)

    params = json.loads(msg['offer'])
    remote_offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    # Handle offer
    await peerConnection.setRemoteDescription(remote_offer)

    # Create answer
    answer = await peerConnection.createAnswer()
    await peerConnection.setLocalDescription(answer)

    # Send answer
    await ws.send(json.dumps(
        { 'offer': {"sdp": answer.sdp, "type": answer.type} }
    ))

    def log_info(msg, *args):
        print(pc_id + ' ' + msg, *args)
    
    log_info('Created for %s', remote)

    @peerConnection.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @peerConnection.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info(f"Connection state is {peerConnection.connectionState}")
        if peerConnection.connectionState == "failed":
            await peerConnection.close()
            pcs.discard(peerConnection)

async def ice_handler(ice, ws):
    print(ice)
    print()
    await peerConnection.addIceCandidate(clsprops(ice))
    None

# handle message from client
async def msg_handler(ws, msg, remote):
    msg = json.loads(msg)
    if 'msg' in msg:
        if msg['msg'] == 'close':
            await ws.close()
        else:
            print('msg', msg['msg'])
            await ws.send(json.dumps({
            'status': 200,
            'msg': msg['msg']
        }))
    elif 'offer' in msg:
        await offer_handler(msg, remote, ws)
        await ws.send(json.dumps({
            'status': 'handle peer connection'
        }))
    elif 'new-ice-candidate' in msg:
        # await peerConnection
        await ice_handler(json.loads(msg['new-ice-candidate']), ws)
        await ws.send(json.dumps({
            'status': 'add ice candidate'
        }))

async def consumer_handler(ws, path):
    host, port = ws.remote_address
    remote = f"{host}:{port}"
    print(f'[Connection open] {remote}')
    async for msg in ws:
        await msg_handler(ws, msg, remote)
    print(f'[Connection close] {host}:{port}')

start_server = websockets.serve(consumer_handler, host, port)
print(f'[MSG] Websocket server listen on {host}:{port}')

# run websocker server
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()