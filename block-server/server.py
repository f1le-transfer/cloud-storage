# WS server that sends messages at random intervals

import asyncio
import websockets
import json

async def consumer_handler(websocket, path):
    async for message in websocket:
        msg = json.loads(message)
        print(msg['msg'])
        if msg['msg'] == 'close':
            await websocket.close()

start_server = websockets.serve(consumer_handler, "127.0.0.1", 5050)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
