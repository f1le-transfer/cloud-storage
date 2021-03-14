import socket 
import threading

# TODO: 
# 1. Saving data in the filesystem like world1_15_12_27.chunk
# 2. Method for receive data

HEADER = 64
PORT = 5050
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        # Get len from header
        data_len  = conn.recv(HEADER).decode(FORMAT)
        if data_len:
            data_len = int(data_len)
            # Rewrite to receive data in chunks ↓
            data = conn.recv(4096).decode(FORMAT)
            if data == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {data}")
            conn.send("Data received".encode(FORMAT))

    conn.close()
        

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()
