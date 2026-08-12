import os, socket, ssl, threading, time, struct, sys

PORT = int(os.environ.get("PEER_PORT", "12345"))
DISCOVERY_PORT = 12346
BROADCAST_INTERVAL = 5

peers = {}
peers_lock = threading.Lock()
discovered = set()
active = None
running = True


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


LOCAL_IP = local_ip()


def send_msg(conn, text):
    data = text.encode()
    conn.sendall(struct.pack(">I", len(data)) + data)


def recv_exact(conn, n):
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def recv_msg(conn):
    header = recv_exact(conn, 4)
    if header is None:
        return None
    (length,) = struct.unpack(">I", header)
    body = recv_exact(conn, length)
    return body.decode() if body is not None else None


def register(conn, ip):
    with peers_lock:
        peers[ip] = conn


def unregister(ip):
    with peers_lock:
        conn = peers.pop(ip, None)
    if conn:
        try:
            conn.close()
        except OSError:
            pass


def prompt():
    sys.stdout.write("> ")
    sys.stdout.flush()


def reader(conn, ip):
    while running:
        try:
            msg = recv_msg(conn)
        except OSError:
            break
        if msg is None:
            break
        sys.stdout.write(f"\n[{ip}] {msg}\n")
        prompt()
    unregister(ip)
    if running:
        sys.stdout.write(f"\n[system] {ip} disconnected\n")
        prompt()


def server_loop():
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.load_cert_chain("cert.pem", "key.pem")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PORT))
    s.listen(5)
    while running:
        s.settimeout(1)
        try:
            raw, addr = s.accept()
        except socket.timeout:
            continue
        except OSError:
            break
        try:
            conn = ctx.wrap_socket(raw, server_side=True)
        except ssl.SSLError:
            raw.close()
            continue
        ip = addr[0]
        register(conn, ip)
        threading.Thread(target=reader, args=(conn, ip), daemon=True).start()
        sys.stdout.write(f"\n[system] {ip} connected\n")
        prompt()
    s.close()


def connect(ip, port=None):
    global active
    if port is None:
        port = PORT
    with peers_lock:
        if ip in peers:
            active = ip
            print(f"[system] already connected to {ip}")
            return
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        raw = socket.create_connection((ip, port), timeout=5)
        conn = ctx.wrap_socket(raw, server_hostname=ip)
    except OSError as e:
        print(f"[system] could not connect to {ip}: {e}")
        return
    register(conn, ip)
    threading.Thread(target=reader, args=(conn, ip), daemon=True).start()
    active = ip
    print(f"[system] connected to {ip} — start typing, /back to return")


def broadcaster():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while running:
        try:
            s.sendto(f"PEER:{LOCAL_IP}".encode(), ("<broadcast>", DISCOVERY_PORT))
        except OSError:
            pass
        time.sleep(BROADCAST_INTERVAL)
    s.close()


def discovery_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", DISCOVERY_PORT))
    while running:
        s.settimeout(1)
        try:
            data, addr = s.recvfrom(1024)
        except socket.timeout:
            continue
        except OSError:
            break
        msg = data.decode(errors="ignore")
        if msg.startswith("PEER:"):
            ip = msg[5:]
            if ip != LOCAL_IP and ip not in discovered:
                discovered.add(ip)
                sys.stdout.write(f"\n[system] discovered {ip}\n")
                prompt()
    s.close()


def main():
    global running, active
    print("PeerLink — encrypted P2P chat")
    print(f"your ip: {LOCAL_IP}")
    print("commands: list | connect <ip> | chat <ip> | /back | help | exit")

    threading.Thread(target=server_loop, daemon=True).start()
    threading.Thread(target=broadcaster, daemon=True).start()
    threading.Thread(target=discovery_listener, daemon=True).start()

    while running:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            break

        if active is not None:
            if line == "/back":
                active = None
                continue
            with peers_lock:
                conn = peers.get(active)
            if conn is None:
                print(f"[system] {active} is no longer connected")
                active = None
                continue
            try:
                send_msg(conn, line)
            except OSError:
                print(f"[system] failed to send to {active}")
                unregister(active)
                active = None
            continue

        parts = line.split(maxsplit=1)
        if not parts:
            continue
        cmd = parts[0]
        if cmd == "exit":
            break
        elif cmd == "help":
            print("list | connect <ip> | chat <ip> | /back | exit")
        elif cmd == "list":
            with peers_lock:
                conn_ips = sorted(peers)
            print("discovered:", ", ".join(sorted(discovered)) or "none")
            print("connected: ", ", ".join(conn_ips) or "none")
        elif cmd == "connect" and len(parts) > 1:
            target = parts[1].strip()
            if ":" in target:
                host, _, p = target.partition(":")
                connect(host.strip(), int(p))
            else:
                connect(target)
        elif cmd == "chat" and len(parts) > 1:
            ip = parts[1].strip()
            with peers_lock:
                ok = ip in peers
            if ok:
                active = ip
                print(f"[system] chatting with {ip} — /back to return")
            else:
                print(f"[system] not connected to {ip}")
        else:
            print("[system] unknown command")

    running = False
    print("\n[system] shutting down")


if __name__ == "__main__":
    main()