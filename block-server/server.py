import socket 
import threading
import os

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
def send_header(conn, _chunk_name):
  _header = header(f"Chunk-name: {_chunk_name}\nContent-length: {0}")
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

def send(conn, msg, req_type, file_size, path_file = None):
  file_size = "Content-length: {0}\n".format(file_size)
  _header = "TCP {0}\nChunk-name: {1}\n".format(req_type, path_file)
    
  if file_size:
    conn.send(header(_header + file_size))
  else:
    conn.send(header(_header + "File-path: {0}".format(path_file)))
  
  if msg:
    msg = msg.encode(FORMAT)
    conn.send(msg)

# Send chunk
def send_file(conn, name, req_type, chunk_name):
  size = os.path.getsize(name)
  f = open(name, '+r')
  l = f.read(BUF_SIZE)
  while (l):
    send(conn, l, req_type, size, chunk_name)
    l = f.read(BUF_SIZE)
  f.close()

def handle_client(conn, addr):
  print(f"\n[NEW CONNECTION] {addr} connected.\n")
  _method = _chunk_name = None
  isok = True
  
  while True:
    # Get data from client
    header = conn.recv(HEADER).decode(FORMAT)
    if not header: break
    
    header = [h.strip() for h in header.split("\n")]
    
    _chunk_name = parase_header(header)["chunk_name"]
    _method = parase_header(header)["method"]
    
    if _method == "POST":
      data = conn.recv(BUF_SIZE).decode(FORMAT)
      if not data: break
    
      # Save data in file
      save_file(_chunk_name, data)
    elif _method == "GET":
#      send_header(conn, _chunk_name)
      send_file(conn, _chunk_name, "GET", _chunk_name)
      break
    else:
      isok = False
      break
  conn.close()
  
  conn.close()
  if isok:
    if _method == "POST":
      print(f"[LOG] Method: {_method}. File \"{_chunk_name}\" saved.")
    else:
      print(f"[LOG] Method: {_method}. File \"{_chunk_name}\" sent.")
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
