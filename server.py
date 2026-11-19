
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((HOST, PORT))
server.listen(1)

print("================================")
print("       LAN BUDDY SERVER")
print("================================")
print("Waiting for a client...")

client, address = server.accept()

print("Client connected:", address)
print("You can start chatting!")
print("--------------------------------")

stop_event = threading.Event()


def receive_messages():
    while not stop_event.is_set():
        try:
            data = client.recv(1024)

            if not data:
                print("\nClient disconnected.")
                break

            message = data.decode()

            if message.lower() == "exit":
                print("\nClient left the chat.")
                break

            print("\nClient:", message)

        except OSError:
            break

    stop_event.set()


thread = threading.Thread(
    target=receive_messages,
    daemon=True
)

thread.start()

try:
    while not stop_event.is_set():
        message = input("You: ")

        if stop_event.is_set():
            break

        client.sendall(message.encode())

        if message.lower() == "exit":
            break

except (OSError, EOFError):
    print("\nConnection ended.")

finally:
    stop_event.set()

    try:
        client.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass

    client.close()
    server.close()

    print("Server closed.")
