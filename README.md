# LAN Buddy

A modern dark-themed web chat built on Python TCP sockets.

**Stack:** Python, Flask, TCP sockets, HTML, CSS, JavaScript

## How it works

```
Browser ──HTTP/JSON──► app.py (Flask) ──TCP──► server.py ◄──TCP── client.py
```

- `server.py`: TCP chat server that broadcasts messages to everyone
- `client.py`: terminal chat client
- `app.py`: Flask app that opens a TCP socket for each web user
- `templates/` and `static/`: the web interface

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

## Run

Open three terminals in the project folder:

```bash
python server.py     # 1. TCP chat server (port 9999)
python app.py        # 2. Web app (port 5000)
python client.py     # 3. optional terminal client
```

Then open http://127.0.0.1:5000 in your browser.

## Using it over a LAN

1. Run `server.py` on one computer and find its LAN IP (`ipconfig` or `ifconfig`).
2. On other computers, run `app.py` and enter that IP on the connect screen.
3. Allow Python through the firewall if asked.

## Screenshots

Add images to the `screenshots/` folder and link them here.