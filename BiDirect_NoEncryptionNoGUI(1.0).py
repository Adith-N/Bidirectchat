#Chat - encryption AES required
import socket
import threading
import os
os.system("color 0A")
# Server Establishment - can use radmin VPN to create pseudonetwork
def server():
    s = socket.socket()
    s.bind(('0.0.0.0', 6000))  # listen on port 6000
    s.listen(1)
    print("[Server] Waiting for connection on port 6000...")
    conn, addr = s.accept()
    print("[Server] Connected by", addr)
    while True:
        data = conn.recv(1024)
        if data:
            print("\n[Server received]:", data.decode())
        else:
            break

# Client Establishment - target ip will be of recieving server..
def client():
    target_ip = input("Enter peer IP to connect as client: ")
    c = socket.socket()
    c.connect((target_ip, 6000))
    print("[Client] Connected to", target_ip)
    while True:
        msg = input("[Client send]: ")
        c.send(msg.encode())

if __name__ == '__main__':
    # Start server thread
    threading.Thread(target=server, daemon=True).start()
    # Start client in main thread
    client()

