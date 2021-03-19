import socket 
import threading

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

# Create header
def header(data):
  data = str(data).encode(FORMAT)
  data +=  b' ' * (HEADER - len(data))
  return data

# Send header
def send_msg(conn, _chunk_name):
  _header = header(f"Connection: close\nChunk-name: {_chunk_name}")
  conn.send(_header)

# Parse header to the object
def parase_header(header):
  header_obj = {}
  for i in header:
    if i.find("Chunk-name") > -1:
      header_obj["chunk_name"] = i[i.find("Chunk-name")+len("Chunk-name: "):].strip()
    if i.find("TCP") > -1:
      header_obj["method"] = i[i.find("TCP")+len("TCP "):].strip()
  return header_obj

# Write data to the file
def save_file(user_file, data):
  with open(user_file, "+w") as f:
    f.write(data)

def handle_client(conn, addr):
  print(f"\n[NEW CONNECTION] {addr} connected.\n")
  _method = _chunk_name = None
  isok = True
  
  while True:
    # Get data from client
    header = conn.recv(HEADER).decode(FORMAT)
    data = conn.recv(BUF_SIZE).decode(FORMAT)
    
    header = [h.strip() for h in header.split("\n")]
        
    if not data or not header: break
        
    _chunk_name = parase_header(header)["chunk_name"]
    _method = parase_header(header)["method"]
    
    if _method == "POST":
      # Save data in file
      save_file(_chunk_name, data)
    else:
      isok = False
      break
  
  conn.close()
  if isok:
    print(f"[LOG] File {_chunk_name} saved. Method: {_method}")
  else:
    print(f"[LOG] Wrong method \"{_method}\" for {_chunk_name}")

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
