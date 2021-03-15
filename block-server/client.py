# Client example
import socket

HEADER = 64
BUF_SIZE = 4096
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def header(data):
  data = str(data).encode(FORMAT)
  data +=  b' ' * (HEADER - len(data))
  return data

def send(msg, req_type):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    
    # Send headers message length and type request
    client.send(header(msg_length))
    client.send(header(req_type))

    client.send(message)
    print(client.recv(BUF_SIZE).decode(FORMAT))

req_type = input('request type? ')
file_name = input('file name? ')

# Trasfer file
def handle_file(name, req_type):
  f = open(name, '+r')
  l = f.read(BUF_SIZE)
  while (l):
    send(l, req_type)
    l = f.read(BUF_SIZE)
  f.close()

handle_file(file_name, req_type)

# Close connection
send(DISCONNECT_MESSAGE, 'POST')
client.close()
