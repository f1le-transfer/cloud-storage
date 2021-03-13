import socket
import os

HOST = "127.0.0.1"
PORT = 8080
#BUF_SIZE = 4096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

while 1:
  conn, addr = s.accept()
  print(f"Conn by {addr}")
  
  conn.send(bytes('Hello, World!\n', 'utf-8'))
  # close client connection
  conn.close() 
  print()

s.close() 
