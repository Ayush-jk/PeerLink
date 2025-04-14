import socket, ssl, threading, json
from datetime import datetime

peer_registry, registry_lock = {}, threading.Lock()

def handle_client(ssl_sock, addr):
    try:
        data = ssl_sock.recv(1024).decode()
        if data.startswith("REGISTER"):
            try:
                port = int(data.split()[1])
                peer_address = (addr[0], port)
                with registry_lock: peer_registry[peer_address] = datetime.now().timestamp()
                print(f"[REGISTERED] Peer {peer_address}")
                ssl_sock.sendall(b"REGISTERED")
            except (IndexError, ValueError): ssl_sock.sendall(b"ERROR: Invalid format")
        elif data == "DISCOVER":
            current_time = datetime.now().timestamp()
            with registry_lock:
                stale_peers = [p for p, t in peer_registry.items() if current_time - t > 300]
                for peer in stale_peers: del peer_registry[peer]
                active_peers = list(peer_registry.keys())
            ssl_sock.sendall(json.dumps(active_peers).encode())
            print(f"[DISCOVERY] Sent {len(active_peers)} peers to {addr}")
        elif data == "DEREGISTER":
            with registry_lock:
                for key in list(peer_registry.keys()):
                    if key[0] == addr[0]: del peer_registry[key]
            ssl_sock.sendall(b"DEREGISTERED")
        else: ssl_sock.sendall(b"ERROR: Unknown command")
    except Exception as e: print(f"[ERROR] {e}")
    finally: ssl_sock.close()

def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('127.0.0.1', 12345)  # Changed to listen on all interfaces
    server_socket.bind(server_address)
    server_socket.listen(5)
    print(f"[STARTING] Discovery server started on {server_address[0]}:{server_address[1]}...")
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"[NEW CONNECTION] {addr}")
            try:
                ssl_client_socket = context.wrap_socket(client_socket, server_side=True)
                client_thread = threading.Thread(target=handle_client, args=(ssl_client_socket, addr))
                client_thread.daemon = True
                client_thread.start()
            except ssl.SSLError as e:
                print(f"[SSL ERROR] {e}")
                client_socket.close()
    except KeyboardInterrupt: print("\n[STOPPING] Server shutting down...")
    finally: server_socket.close()

if __name__ == "__main__": start_server()