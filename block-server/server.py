import socket 
import threading

# TODO: 
# 1. Saving data in the filesystem like world1_15_12_27.chunk
# 2. Method for receive data

HEADER = 64
BUF_SIZE = 4096
PORT = 5050
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def save_file(user_file, data):
  with open(user_file, "+w") as f:
    f.write(data) 

def handle_client(conn, addr):
  print(f"[NEW CONNECTION] {addr} connected.\n")

  connected = True
  while connected:
    data_len = conn.recv(HEADER).decode(FORMAT).strip()
    req_type = conn.recv(HEADER).decode(FORMAT).strip()
    print(f'Len: {data_len} {req_type}')
    if data_len:
      data = conn.recv(BUF_SIZE).decode(FORMAT)
      print(f"[{addr}] {data}")
      if data == DISCONNECT_MESSAGE:
        connected = False
      else:
        save_file('server_test.txt', data)
      conn.send("Data received".encode(FORMAT))

  conn.close()
        

def start():
  server.listen()
  print(f"[LISTENING] Server is listening on {SERVER}")
  while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}\n")


print("[STARTING] server is starting...")
start()

