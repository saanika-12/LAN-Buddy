# LAN Buddy – Python Client-Server Chat Application

## Project Overview

LAN Buddy is a simple two-way text chat application developed using Python socket programming. It allows two computers connected through the same network to communicate with each other using a client-server architecture.

One computer acts as the server, while another connects as the client.

## Objectives

- Understand client-server architecture.
- Learn socket programming in Python.
- Understand IP addresses and port numbers.
- Establish TCP connections.
- Exchange messages between two computers.
- Understand basic network communication.

## Technologies Used

- Python 3
- TCP/IP
- Socket Programming
- Threading
- Visual Studio Code

## Features

- Two-way text communication.
- Client-server architecture.
- TCP-based communication.
- IP address and port configuration.
- Simultaneous sending and receiving.
- Graceful disconnection.

## Project Structure

```text
LAN-Buddy/
│
├── server.py
├── client.py
├── README.md
├── requirements.txt
├── .gitignore
└── screenshots/
```

## How to Run

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
```

### 2. Open the project folder

```bash
cd LAN-Buddy
```

### 3. Start the server

```bash
python server.py
```

### 4. Start the client

Open another terminal and execute:

```bash
python client.py
```

### 5. Enter the server IP address

For testing on the same computer, enter:

```text
127.0.0.1
```

For communication between two computers, enter the server computer's local IP address.

## Working

1. The server creates a TCP socket.
2. The server binds to an IP address and port number.
3. The server listens for incoming connections.
4. The client creates a socket and connects to the server.
5. Both sides exchange messages.
6. Threading allows messages to be received in the background while typing.
7. The connection closes when a user enters the exit command.

## Expected Output

A successful connection between the client and server, followed by two-way text message exchange.

## Learning Outcomes

This project demonstrates basic client-server communication, socket creation, TCP connection establishment, and message transmission over a network.

## Developed By

Add your team members' names and USNs here.

## License

This project is developed for educational purposes.