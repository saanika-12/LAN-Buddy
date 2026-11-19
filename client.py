import os
import socket
import threading

HOST = "127.0.0.1"   # change to the server's LAN IP to chat across computers
PORT = 9999


def receive(sock):
    """Print every message the server sends us."""
    reader = sock.makefile("r", encoding="utf-8")
    for line in reader:
        parts = line.rstrip("\n").split("|", 2)
        if len(parts) < 3:
            continue
        kind, sender, text = parts
        if kind == "MSG":
            print(f"\n[{sender}] {text}")
        else:
            print(f"\n* {text}")
    print("\nDisconnected from server. Press Enter to exit.")
    os._exit(0)  # stop the program even though input() is waiting


def main():
    username = input("Choose a username: ").strip()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))
    except OSError:
        print(f"Could not connect to {HOST}:{PORT}. Is server.py running?")
        return

    sock.sendall((username + "\n").encode("utf-8"))
    threading.Thread(target=receive, args=(sock,), daemon=True).start()

    print("Connected! Type a message and press Enter. Type /quit to leave.")
    while True:
        try:
            text = input()
        except (EOFError, KeyboardInterrupt):
            break
        if text == "/quit":
            break
        if text:
            sock.sendall((text + "\n").encode("utf-8"))

    sock.close()


if __name__ == "__main__":
    main()