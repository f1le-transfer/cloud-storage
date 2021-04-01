import asyncio
import websockets
import json

async def handle(websocket, msg):  
  if 'header' in msg: 
    print('Header:', msg)  
  elif 'msg' in msg:
    if msg['msg'] == 'close':
      await websocket.close()
    else:
      if len(msg['msg']) < 250:
        print(msg['msg'])
        await websocket.send(json.dumps({'status': '200', 'msg': msg['msg']}))
      else:
        print('Msg received.')
        await websocket.send(json.dumps({'status': '200', 'msg': 'Msg recv.'}))


async def consumer_handler(websocket, path):
  host, port = websocket.remote_address
  print(f'[Connection open] {host}:{port}')
  async for message in websocket:
    print(len(message))
    print()
    msg = json.loads(message)
    await handle(websocket, msg)                
  print(f'[Connection close] {host}:{port}')

start_server = websockets.serve(consumer_handler, host="127.0.0.1", port=5050, read_limit=4096, max_size=4096, max_queue=10)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
