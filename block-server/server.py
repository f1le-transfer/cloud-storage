import json
import asyncio
import websockets
import uuid
import time

from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling

host = '127.0.0.1'
port = 5050
# set of ...
pcs = set()
peerConnection = None

# 1. offer
# 2. Ice candidate
# 3. close connection

async def consume_singaling(ws, msg):
    if 'offer' in msg:
        params = json.loads(msg['offer'])
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
        await peerConnection.setRemoteDescription(offer)
        await peerConnection.setLocalDescription(await peerConnection.createAnswer())
        
        await ws.send(json.dumps({ 'offer': peerConnection.localDescription.__dict__ }))
    elif 'new-ice-candidate' in msg:
        candidate = json.loads(msg['new-ice-candidate'])
        candidate = RTCIceCandidate(candidate)
        print(candidate)
        print()
        await peerConnection.addIceCandidate(candidate=candidate)
        

async def run_answer(ws, msg):
    global peerConnection
    peerConnection = RTCPeerConnection()

    @peerConnection.on("datachannel")
    def on_datachannel(channel):
        start = time.time()
        octest = 0

        @channel.on("message")
        async def on_message(msg):
            nonlocal octest

            if msg:
                octest += len(msg)
            else:
                elapsed = time.time() - start
                print(
                    "received %d bytes in %.1f s (%.3f Mbps)"
                    % (octest, elapsed, octest * 8 / elapsed / 1000000)
                )

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
    elif 'peerConnection' in msg:
        await run_answer(ws, msg)
    elif 'offer' in msg or 'new-ice-candidate' in msg:
        await consume_singaling(ws, msg)

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