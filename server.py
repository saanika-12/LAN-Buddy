import socket
import threading

HOST = "0.0.0.0"   # listen on all network interfaces (needed for LAN use)
PORT = 9999

clients = {}                    # socket -> username
clients_lock = threading.Lock() # protects the dictionary across threads


def broadcast(kind, sender, text):
    """Send one message line to every connected client."""
    line = f"{kind}|{sender}|{text}\n".encode("utf-8")
    with clients_lock:
        for sock in list(clients):
            try:
                sock.sendall(line)
            except OSError:
                pass  # that client is gone; its own thread will clean up


def send_to(sock, kind, text):
    """Send a server message to just one client."""
    try:
        sock.sendall(f"{kind}|server|{text}\n".encode("utf-8"))
    except OSError:
        pass


def handle_client(conn, addr):
    """Runs in its own thread, one per connected client."""
    try:
        reader = conn.makefile("r", encoding="utf-8")

        # First line from a client is always its username
        username = reader.readline().replace("|", "").strip()[:20]
        if not username:
            return

        with clients_lock:
            taken = username in clients.values()
            if not taken:
                clients[conn] = username

        if taken:
            send_to(conn, "ERR", "That username is already taken")
            return

        send_to(conn, "OK", "Welcome to LAN Buddy!")
        broadcast("SYS", "server", f"{username} joined the chat")
        print(f"[+] {username} connected from {addr[0]}")

        # Every following line is a chat message
        for line in reader:
            text = line.strip()
            if text:
                broadcast("MSG", username, text)

    except OSError:
        pass  # connection dropped suddenly
    finally:
        with clients_lock:
            left_user = clients.pop(conn, None)
        conn.close()
        if left_user:
            print(f"[-] {left_user} disconnected")
            broadcast("SYS", "server", f"{left_user} left the chat")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"LAN Buddy server listening on port {PORT} (Ctrl+C to stop)")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.close()


if __name__ == "__main__":
    main()