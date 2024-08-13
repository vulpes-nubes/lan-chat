import socket
import threading

# Server code
def handle_client(client_socket):
    """Handle a single client connection."""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"[{client_socket.getpeername()}] {message}")
                broadcast(message, client_socket)
            else:
                break
        except:
            break

    client_socket.close()

def broadcast(message, client_socket):
    """Broadcasts the message to all clients except the sender."""
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                clients.remove(client)

def start_server():
    """Starts the server and listens for incoming connections."""
    server.listen()
    print(f"[INFO] Server listening on {SERVER}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

def udp_broadcast_listener():
    """Listens for UDP broadcasts and responds to clients searching for servers."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind((SERVER, BROADCAST_PORT))

    print(f"[INFO] UDP broadcast listener started on port {BROADCAST_PORT}")
    
    while True:
        message, client_addr = udp_socket.recvfrom(1024)
        if message.decode('utf-8') == "DISCOVER_SERVER":
            response = f"{SERVER}:{PORT}"
            udp_socket.sendto(response.encode('utf-8'), client_addr)

if __name__ == "__main__":
    SERVER = socket.gethostbyname(socket.gethostname())  # Get the local machine IP
    PORT = 5555
    BROADCAST_PORT = 5556

    clients = []

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER, PORT))

    # Start the TCP server thread
    print("[STARTING] Server is starting...")
    threading.Thread(target=start_server).start()

    # Start the UDP broadcast listener thread
    threading.Thread(target=udp_broadcast_listener).start()
