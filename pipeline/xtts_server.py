import socket

# 1. Create a socket (AF_INET = IPv4, SOCK_STREAM = TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. Bind the socket to an address and port
# Use '' or '0.0.0.0' to listen on all available network interfaces
server_socket.bind(('127.0.0.1', 8080))

# 3. Enable the server to accept connections
# The argument is the 'backlog' (max number of queued connections)
server_socket.listen(5)

print("Server is listening on 127.0.0.1:8080...")

while True:
    # 4. Accept a new connection
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address}")
    
    # 5. Handle the connection (e.g., receive and send data)
    data = client_socket.recv(1024)
    client_socket.send(b"Hello from the server!")
    client_socket.close()