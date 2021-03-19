import socket 
import threading
#from TCP_STATUSES import TCP_STATUSES

# TODO: 
# 1. Saving data in the filesystem like world1_15_12_27.chunk

HEADER = 128
BUF_SIZE = 4096
PORT = 5050
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def save_file(user_file, data):
  with open(user_file, "+w") as f:
    f.write(data) 

def header(data):
  data = str(data).encode(FORMAT)
  data +=  b' ' * (HEADER - len(data))
  return data

def chunk_name(header):
  for i in header:
    if i[:11] == "Chunk-name:":
      return i[11:].strip()

def send_msg(conn, _chunk_name):
  _header = header(f"Connection: close\nChunk-name: {_chunk_name}")
  conn.send(_header)
    

def handle_client(conn, addr):
  print(f"\n[NEW CONNECTION] {addr} connected.\n")
  _chunk_name = None
  while True:
    # Get data from client
    header = conn.recv(HEADER).decode(FORMAT)
    data = conn.recv(BUF_SIZE).decode(FORMAT)
    
    header = [h.strip() for h in header.split("\n")]
        
    if not data or not header: break
        
    # Save data in file
    _chunk_name = chunk_name(header)
    save_file(_chunk_name, data)
  
#  send_msg(conn, _chunk_name)
  conn.close()
  print(f"[LOG] File {_chunk_name} saved.")

# Strart server
def start():
  server.listen()
  print(f"[LISTENING] Server is listening on {SERVER}")
  while True:
    conn, addr = server.accept()
    # Create new process for every client
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()
