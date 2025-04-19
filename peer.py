import socket, ssl, threading, time, sys

PORT, BROADCAST_PORT, BUFFER_SIZE = 12345, 12346, 1024
running, chat_mode, current_chat = True, False, None
discovered_peers = set()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return socket.gethostbyname(socket.gethostname())

LOCAL_IP = get_local_ip()

def create_ssl_context():
    c = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    c.load_cert_chain("cert.pem", "key.pem")
    c.check_hostname, c.verify_mode = False, ssl.CERT_NONE
    return c

def handle_connection(conn, addr):
    global current_chat, chat_mode
    try:
        while running:
            data = conn.recv(BUFFER_SIZE)
            if not data: break
            print(f"[{addr}] -> {data.decode()}")
            try: conn.send(b"Message received")
            except: pass
            if chat_mode:
                print(f"[Chat with {current_chat}] Type your message: ", end="", flush=True)
            else:
                print("\nCommand: ", end="", flush=True)
    except Exception as e:
        print(f"\n[Error] Connection with {addr} closed: {e}")
    finally:
        conn.close()
        if chat_mode and current_chat == addr:
            chat_mode, current_chat = False, None
            print("\nCommand: ", end="", flush=True)

def server_thread():
    context = create_ssl_context()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(('0.0.0.0', PORT))
        s.listen(5)
        print(f"[System] Listening on port {PORT}")
        while running:
            try:
                s.settimeout(1)
                conn, addr = s.accept()
                conn = context.wrap_socket(conn, server_side=True)
                print(f"\n[System] Connection from {addr[0]}")
                threading.Thread(target=handle_connection, args=(conn, addr[0]), daemon=True).start()
            except socket.timeout:
                continue
    except Exception as e:
        print(f"[Error] Server error: {e}")
    finally:
        s.close()

def connect_to_peer(ip):
    global current_chat, chat_mode
    try:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
        sock = socket.create_connection((ip, PORT), timeout=5)
        conn = ctx.wrap_socket(sock, server_hostname=ip)
        print(f"[System] Connected to {ip}")
        current_chat, chat_mode = ip, True

        while running and chat_mode:
            msg = input(f"[Chat with {ip}] Type your message: ")
            if msg.lower() in ('exit', 'quit', 'bye', '/exit', '/quit', '/bye'):
                break
            try:
                conn.send(msg.encode())
                reply = conn.recv(BUFFER_SIZE).decode()
                print(f"[{ip}] -> {reply}")
            except:
                break
    except Exception as e:
        print(f"[Error] Could not connect to {ip}: {e}")
    finally:
        try: conn.close()
        except: pass
        if chat_mode and current_chat == ip:
            chat_mode, current_chat = False, None
            print("\nCommand: ", end="", flush=True)

def broadcast_presence():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        s.sendto(f"PEER:{LOCAL_IP}".encode(), ('<broadcast>', BROADCAST_PORT))
        print(f"[System] Broadcast sent: {LOCAL_IP}")
    except Exception as e:
        print(f"[Error] Broadcast failed: {e}")
    finally:
        s.close()

def listen_for_broadcasts():
    global discovered_peers
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(('', BROADCAST_PORT))
        print(f"[System] Listening for broadcasts on {BROADCAST_PORT}")
        while running:
            try:
                s.settimeout(1.0)
                data, addr = s.recvfrom(BUFFER_SIZE)
                msg = data.decode()
                if msg.startswith("PEER:"):
                    peer_ip = msg[5:]
                    if peer_ip != LOCAL_IP and peer_ip not in discovered_peers:
                        discovered_peers.add(peer_ip)
                        print(f"\n[System] Discovered: {peer_ip}")
                        print("Command: ", end="", flush=True)
            except socket.timeout:
                continue
    except Exception as e:
        print(f"[Error] Broadcast listen error: {e}")
    finally:
        s.close()

def show_help():
    print("\n=== COMMANDS ===")
    print("connect <IP> - Start chat")
    print("list         - Show peers")
    print("broadcast    - Discover peers")
    print("exit         - Quit")
    print("help         - Help\n")

def main():
    global running
    print("\n=== P2P SECURE MESSAGING SYSTEM ===")
    print(f"Your IP: {LOCAL_IP}\nType 'help' for commands")

    threading.Thread(target=server_thread, daemon=True).start()
    threading.Thread(target=listen_for_broadcasts, daemon=True).start()

    while running:
        if not chat_mode:
            try:
                cmd = input("\nCommand: ").strip().lower()
                if cmd == 'exit':
                    running = False
                    break
                elif cmd == 'help':
                    show_help()
                elif cmd == 'broadcast':
                    broadcast_presence()
                elif cmd == 'list':
                    if discovered_peers:
                        print("\n=== DISCOVERED PEERS ===")
                        for i, p in enumerate(discovered_peers, 1):
                            print(f"{i}. {p}")
                        print("========================")
                    else:
                        print("[System] No peers discovered")
                elif cmd.startswith('connect '):
                    ip = cmd.split(' ', 1)[1].strip()
                    if ip:
                        threading.Thread(target=connect_to_peer, args=(ip,), daemon=True).start()
                    else:
                        print("[Error] Specify an IP")
                else:
                    print("[Error] Unknown command")
            except KeyboardInterrupt:
                running = False
                break
            except Exception as e:
                print(f"[Error] {e}")
    print("[System] Shutting down...")

if __name__ == "__main__":
    main()
