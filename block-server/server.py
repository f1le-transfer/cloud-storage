import socket
import os

HOST = "127.0.0.1"
PORT = 8080
#BUF_SIZE = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

def send_msg(conn, msg):
  msg = bytes(msg+'\n', 'utf-8')
  conn.send(msg)

while 1:
  conn, addr = s.accept()
  print(f"Client: {addr[0]}:{addr[1]}")

  #conn.send(bytes('Hello, World!\n', 'utf-8'))
  send_msg(conn, 'Hello, World!')  

  # close client connection
  conn.close()
  print()

s.close() 
