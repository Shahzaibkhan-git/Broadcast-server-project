# Project Page URL
https://roadmap.sh/projects/broadcast-server

# Broadcast Server (Python + WebSockets)

A simple CLI-based broadcast server where multiple clients can connect, send messages, and receive messages in real time.

## Features

- Start a WebSocket server from CLI
- Connect multiple clients from CLI
- Register client names with `--name`
- Broadcast each incoming message to all connected clients
- Show messages as `name: message`
- Broadcast join/leave notifications
- Handle client disconnects gracefully
- Basic graceful shutdown with `Ctrl+C`

## Tech Stack

- Python 3.10+
- `asyncio`
- `websockets`

## Project Structure

```text
.
├── pyproject.toml        # Packaging config + CLI entry point
├── build_backend.py      # Lightweight build backend (no external tooling)
├── cli.py      # CLI entrypoint (start/connect commands)
├── server.py   # WebSocket server and broadcasting logic
└── client.py   # Interactive client (send + receive)
```

## Setup

1. Create virtual environment (if not already created):

```bash
python3 -m venv .venv
```

2. Activate virtual environment:

```bash
source .venv/bin/activate
```

3. Install the project in editable mode (creates the `broadcast-server` command and installs dependencies):

```bash
pip install -e .
```

## Usage

### 1) Start server

```bash
broadcast-server start --host 127.0.0.1 --port 8765
```

### 2) Connect clients

Open two separate terminals and run:

```bash
broadcast-server connect --host 127.0.0.1 --port 8765 --name alice
```

```bash
broadcast-server connect --host 127.0.0.1 --port 8765 --name bob
```

Type messages in either client. The server will broadcast to all connected clients.
Each client uses its configured `--name`, and messages appear as `name: message`.

Use `/quit` or `/exit` to disconnect a client.

## CLI Reference

### Server command

```bash
broadcast-server start [--host HOST] [--port PORT]
```

- `--host` default: `127.0.0.1`
- `--port` default: `8765`

### Client command

```bash
broadcast-server connect [--host HOST] [--port PORT] [--name NAME]
```

- `--host` default: `127.0.0.1`
- `--port` default: `8765`
- `--name` default: `anonymous`

## Expected Behavior

- When a client connects/disconnects, server logs current client count.
- When a client joins, others receive: `<name> joined the chat`.
- When a client leaves, others receive: `<name> left the chat`.
- When a message is sent, all connected clients receive: `<name>: <message>`.
- Pressing `Ctrl+C` on the server stops it and closes client connections.

## Troubleshooting

- `Could not connect to server`: make sure server is running on the same host/port.
- `Address already in use`: choose another port with `--port`.
- If one terminal appears stuck, check if it is waiting for user input (`> ` prompt).
- If you still see old output like `127.0.0.1:... -> __name__:alice`, restart from current code:

```bash
source .venv/bin/activate
pkill -f "broadcast-server start" || true
pkill -f "python cli.py start" || true
pip uninstall -y broadcast-server
pip install -e .
```
