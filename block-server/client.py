# Client example
import socket
import os

HEADER = 64
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

def send(msg, req_type, file_size):
    msg = msg.encode(FORMAT)

    _header = header(f"Connection: keep-alive\nContent-length: {file_size}")
    
    client.send(_header)
    client.send(msg)
    #print(client.recv(BUF_SIZE).decode(FORMAT))

req_type = input('request type? ')
file_name = input('file name? ')
print()

# Trasfer file
def handle_file(name, req_type):
  size = os.path.getsize(name)
  f = open(name, '+r')
  l = f.read(BUF_SIZE)
  while (l):
    send(l, req_type, size)
    l = f.read(BUF_SIZE)
  f.close()

handle_file(file_name, req_type)

client.close()
