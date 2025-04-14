import socket, ssl, threading, json, random, os

running, username, peer_port = True, None, None
SERVER_IP = '127.0.0.1'  # Use localhost for testing on single machine

def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')

def handle_peer(ssl_sock, addr):
    try:
        print(f"\n[CONNECTED] {addr} joined")
        print("Type message (or 'exit'): ", end="", flush=True)
        while running:
            data = ssl_sock.recv(1024).decode()
            if not data: break
            print(f"\r{addr[0]}: {data}")
            print("You: ", end="", flush=True)
    except Exception as e:
        if running: print(f"\n[ERROR] Connection lost: {e}")
    finally:
        ssl_sock.close()
        print(f"\n[DISCONNECTED] {addr} left")
        print("You: ", end="", flush=True)

def listen_for_peers(port):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listener.bind(('0.0.0.0', port))
        listener.listen(5)
        listener.settimeout(1)
        print(f"[LISTENING] Port {port}")
        while running:
            try:
                client, addr = listener.accept()
                ssl_client = context.wrap_socket(client, server_side=True)
                thread = threading.Thread(target=handle_peer, args=(ssl_client, addr))
                thread.daemon = True
                thread.start()
            except socket.timeout: continue
            except Exception as e:
                if running: print(f"[ERROR] {e}")
    except Exception as e: print(f"[CRITICAL] Listener failed: {e}")
    finally: listener.close()

def connect_to_server(cmd):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname, context.verify_mode = False, ssl.CERT_NONE
    try:
        with socket.create_connection((SERVER_IP, 12345)) as sock:
            with context.wrap_socket(sock, server_hostname=SERVER_IP) as ssl_sock:
                ssl_sock.send(cmd.encode())
                return ssl_sock.recv(4096).decode()
    except Exception as e:
        print(f"[ERROR] Server connection: {e}")
        return None

def register(port):
    response = connect_to_server(f"REGISTER {port}")
    return response == "REGISTERED"

def discover_peers():
    response = connect_to_server("DISCOVER")
    return json.loads(response) if response else []

def connect_to_peer(ip, port):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname, context.verify_mode = False, ssl.CERT_NONE
    try:
        with socket.create_connection((ip, port)) as sock:
            with context.wrap_socket(sock, server_hostname=ip) as ssl_sock:
                print(f"[CONNECTED] Connected to {ip}:{port}")
                thread = threading.Thread(target=handle_peer, args=(ssl_sock, (ip, port)))
                thread.daemon = True
                thread.start()
                while running:
                    msg = input("You: ")
                    if msg.lower() == 'exit': break
                    ssl_sock.send(msg.encode())
    except Exception as e: print(f"[ERROR] {e}")

def main():
    global running, username, peer_port
    clear_screen()
    print("=== Secure P2P Chat ===\n")
    username = input("Username: ")
    peer_port = random.randint(10000, 65000)
    threading.Thread(target=listen_for_peers, args=(peer_port,), daemon=True).start()
    if not register(peer_port): return
    try:
        while True:
            print("\n1. Find peers\n2. Wait for connections\n3. Exit")
            choice = input("Option (1-3): ")
            if choice == '1':
                peers = discover_peers()
                if not peers: print("No peers found"); continue
                print("\nPeers:")
                for i, peer in enumerate(peers): print(f"{i+1}. {peer[0]}:{peer[1]}")
                idx = int(input("Select peer (0 to cancel): ")) - 1
                if idx >= 0: connect_to_peer(peers[idx][0], peers[idx][1])
            elif choice == '2': print(f"[WAITING] Port {peer_port}"); input("Press Enter to return")
            elif choice == '3': break
    except KeyboardInterrupt: print("\n[EXITING]")
    finally:
        running = False
        connect_to_server("DEREGISTER")
        print("[GOODBYE]")

if __name__ == "__main__": main()