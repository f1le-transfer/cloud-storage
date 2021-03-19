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

def header(data):
  data = str(data).encode(FORMAT)
  data +=  b' ' * (HEADER - len(data))
  return data

def send(msg, req_type, file_size, chunk_name):
  msg = msg.encode(FORMAT)

  _header = header(f"Connection: keep-alive\nContent-length: {file_size}\nChunk-name: {chunk_name}")
    
  client.send(_header)
  client.send(msg)
#  print(client.recv(BUF_SIZE).decode(FORMAT))

req_type = input('request type? ')
path_file = input('path to file? ')
chunk_name = input('chunk name? ')+".chunk"

# Trasfer file
def handle_file(name, req_type, chunk_name):
  size = os.path.getsize(name)
  f = open(name, '+r')
  l = f.read(BUF_SIZE)
  while (l):
    send(l, req_type, size, chunk_name)
    l = f.read(BUF_SIZE)
  f.close()

handle_file(path_file, req_type, chunk_name)

client.close()
