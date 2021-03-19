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

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

#reserved_fields = ['TCP', 'OK', 'Content-Length', 'Content-Type', 'Date', 'Server']

def save_file(user_file, data):
  with open(user_file, "+w") as f:
    f.write(data) 

def header(data):  
  return data.encode(FORMAT)

def handle_client(conn, addr):
  print(f"\n[NEW CONNECTION] {addr} connected.")

  connected = True
  while True:
    # Get data from client
    header = conn.recv(HEADER).decode(FORMAT)
    data = conn.recv(BUF_SIZE).decode(FORMAT)
    
    print(header)    

    if not data or not header: break

    # Save data in file
    save_file('a.txt', data)
  
  conn.close()
        
def send_msg(): None

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

