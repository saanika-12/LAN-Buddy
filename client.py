
import socket
import threading

HOST = input("Enter server IP address: ")
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

print("================================")
print("        LAN BUDDY CLIENT")
print("================================")
print("Connected to server!")
print("Start chatting. Type 'exit' to quit.")
print("--------------------------------")

stop_event = threading.Event()


def receive_messages():
    while not stop_event.is_set():
        try:
            data = client.recv(1024)

            if not data:
                print("\nServer disconnected.")
                break

            message = data.decode()

            if message.lower() == "exit":
                print("\nServer left the chat.")
                break

            print("\nServer:", message)

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

    print("Disconnected from server.")
