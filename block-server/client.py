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

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    req = 'POST'.encode(FORMAT)
    req += b' ' * (HEADER - len(req))
    client.send(req)
    client.send(message)
    print(client.recv(BUF_SIZE).decode(FORMAT))

# Trasfer file
file_name = input('file name? ')
f = open(file_name, '+r')
l = f.read(BUF_SIZE)

while (l):
  send(l)
  l = f.read(BUF_SIZE)
f.close()

# Close connection
send(DISCONNECT_MESSAGE)
client.close()
