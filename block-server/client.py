# Client example
import socket
import os

HEADER = 128
BUF_SIZE = 4096
PORT = 5050
FORMAT = 'utf-8'
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

req_type = input('request type? ')

def parase_header(header):
  header_obj = {}
  for i in header:
    if i.find("Chunk-name") > -1:
      header_obj["chunk_name"] = i[i.find("Chunk-name")+len("Chunk-name: "):].strip()
    if i.find("TCP") > -1:
      header_obj["method"] = i[i.find("TCP")+len("TCP "):].strip()
  return header_obj

def header(data):
  data = str(data).encode(FORMAT)
  data +=  b' ' * (HEADER - len(data))
  return data

def send(msg, req_type, file_size, path_file = None):
  file_size = "Content-length: {0}\n".format(file_size)
  _header = "TCP {0}\nChunk-name: {1}\n".format(req_type, path_file)
    
  if file_size:
    client.send(header(_header + file_size))
  else:
    client.send(header(_header + "File-path: {0}".format(path_file)))
  
  if msg:
    msg = msg.encode(FORMAT)
    client.send(msg)

# Trasfer file
def send_file(name, req_type, chunk_name):
  size = os.path.getsize(name)
  f = open(name, '+r')
  l = f.read(BUF_SIZE)
  while (l):
    send(l, req_type, size, chunk_name)
    l = f.read(BUF_SIZE)
  f.close()
  
def save_file(user_file, data):
  with open(user_file, "+w") as f:
    f.write(data)

def get_file(path_chunk, req_type):
  send(None, req_type, None, path_chunk)
  chunk_name = None
  while True:
    _header = client.recv(HEADER).decode(FORMAT)
    _header = parase_header([h.strip() for h in _header.split("\n")])
    data = client.recv(BUF_SIZE).decode(FORMAT)
    
    if not data or not "chunk_name" in _header: break
    
    chunk_name = _header["chunk_name"]
    save_file(chunk_name, data)
  print(f"[LOG] File \"{chunk_name}\" from server saved.")

if req_type.strip() == "POST":
  path_file = input('path to file? ')
  chunk_name = input('chunk name? ')+".chunk"
  send_file(path_file, req_type, chunk_name)
elif req_type.strip() == "GET":
  path_chunk = input('chunk path? ')
  get_file(path_chunk, req_type)

client.close()
