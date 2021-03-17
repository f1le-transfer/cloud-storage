import socket 
import threading
#from TCP_STATUSES import TCP_STATUSES

# TODO: 
# 1. Saving data in the filesystem like world1_15_12_27.chunk

HEADER = 64
BUF_SIZE = 4096
PORT = 5050
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

reserved_fields = ['TCP', 'OK', 'Content-Length', 'Content-Type', 'Date', 'Server']

def save_file(user_file, data):
  with open(user_file, "+w") as f:
    f.write(data) 

def handle_client(conn, addr):
  print(f"[NEW CONNECTION] {addr} connected.\n")

  connected = True
  while True:
    # Receive headers
    data_len = conn.recv(HEADER).decode(FORMAT).strip()
    req_type = conn.recv(HEADER).decode(FORMAT).strip()
    file_name = "NO"#conn.recv(HEADER).decode(FORMAT).strip()
    
      
    if not data_len: break
    print(f'Len: {data_len} {req_type}')
    
    # Get data from client
    data = conn.recv(BUF_SIZE).decode(FORMAT)
    print(f'[{addr}] TCP: {req_type}, FILE: {file_name}, Data from client:\n{data}')
    
    # Save data in file
    #save_file('server_test.txt', data)
    
    # Send message about end of the downloading
    conn.send("Data received".encode(FORMAT))

  conn.close()
        
# Strart server
def start():
  server.listen()
  print(f"[LISTENING] Server is listening on {SERVER}")
  while True:
    conn, addr = server.accept()
    
    # Create new process for every client
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}\n")


print("[STARTING] server is starting...")
start()

