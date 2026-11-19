
import socket
import threading
import time
import uuid

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

sessions = {}  # session_id -> ChatSession


class ChatSession:
    """One browser user = one TCP socket to server.py."""

    def __init__(self, sock, reader, username):
        self.sock = sock
        self.reader = reader
        self.username = username
        self.messages = []
        self.connected = True
        self.lock = threading.Lock()

    def add_message(self, kind, sender, text):
        with self.lock:
            self.messages.append({
                "id": len(self.messages) + 1,
                "kind": kind,
                "sender": sender,
                "text": text,
                "time": time.strftime("%H:%M"),
            })

    def listen(self):
        """Background thread: read lines from the TCP socket."""
        try:
            for line in self.reader:
                parts = line.rstrip("\n").split("|", 2)
                if len(parts) == 3:
                    self.add_message(*parts)
        except OSError:
            pass
        self.connected = False
        self.add_message("SYS", "server", "Disconnected from server")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/connect", methods=["POST"])
def connect():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).replace("|", "").strip()[:20]
    host = str(data.get("host", "")).strip() or "127.0.0.1"

    try:
        port = int(data.get("port", 9999))
    except (TypeError, ValueError):
        return jsonify(error="Port must be a number"), 400
    if not username:
        return jsonify(error="Please enter a username"), 400

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((host, port))
        sock.sendall((username + "\n").encode("utf-8"))
        reader = sock.makefile("r", encoding="utf-8")
        reply = reader.readline().strip().split("|", 2)
    except OSError:
        sock.close()
        return jsonify(error=f"Could not reach {host}:{port}. Is server.py running?"), 502

    if len(reply) < 3 or reply[0] != "OK":
        sock.close()
        message = reply[2] if len(reply) == 3 else "Server closed the connection"
        return jsonify(error=message), 400

    sock.settimeout(None)  # now wait as long as needed for messages
    session = ChatSession(sock, reader, username)
    session_id = uuid.uuid4().hex
    sessions[session_id] = session
    threading.Thread(target=session.listen, daemon=True).start()

    return jsonify(session_id=session_id, username=username, host=host, port=port)


@app.route("/api/send", methods=["POST"])
def send():
    data = request.get_json(silent=True) or {}
    session = sessions.get(data.get("session_id"))
    if session is None or not session.connected:
        return jsonify(error="You are not connected"), 400

    text = str(data.get("text", "")).replace("\n", " ").strip()
    if not text:
        return jsonify(error="Message is empty"), 400

    try:
        session.sock.sendall((text + "\n").encode("utf-8"))
    except OSError:
        session.connected = False
        return jsonify(error="Connection lost"), 400
    return jsonify(ok=True)


@app.route("/api/messages")
def messages():
    session = sessions.get(request.args.get("session_id"))
    if session is None:
        return jsonify(error="Session expired", connected=False), 404

    since = request.args.get("since", 0, type=int)
    with session.lock:
        new_messages = [m for m in session.messages if m["id"] > since]
    return jsonify(messages=new_messages, connected=session.connected)


@app.route("/api/disconnect", methods=["POST"])
def disconnect():
    data = request.get_json(silent=True) or {}
    session = sessions.pop(data.get("session_id"), None)
    if session:
        session.connected = False
        try:
            session.sock.close()
        except OSError:
            pass
    return jsonify(ok=True)


if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

