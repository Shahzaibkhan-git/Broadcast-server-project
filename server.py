from __future__ import annotations

import asyncio
from typing import Dict, Set

import websockets
from websockets.exceptions import ConnectionClosed

connected_clients: Set[websockets.WebSocketServerProtocol] = set()
client_names: Dict[websockets.WebSocketServerProtocol, str] = {}
clients_lock = asyncio.Lock()


async def register_client(websocket: websockets.WebSocketServerProtocol) -> None:
    async with clients_lock:
        connected_clients.add(websocket)
        client_names[websocket] = "anonymous"
    print(f"Client connected. Total clients: {len(connected_clients)}")


async def unregister_client(websocket: websockets.WebSocketServerProtocol) -> None:
    async with clients_lock:
        connected_clients.discard(websocket)
        name = client_names.pop(websocket, "anonymous")
    print(f"Client disconnected. Total clients: {len(connected_clients)}")
    await broadcast_message(f"{name} left the chat")


async def broadcast_message(message: str) -> None:
    async with clients_lock:
        clients = list(connected_clients)

    if not clients:
        return

    results = await asyncio.gather(
        *(client.send(message) for client in clients),
        return_exceptions=True,
    )

    dead_clients = []
    for client, result in zip(clients, results):
        if isinstance(result, Exception):
            dead_clients.append(client)

    if dead_clients:
        async with clients_lock:
            for client in dead_clients:
                connected_clients.discard(client)
                client_names.pop(client, None)


async def handle_client(websocket: websockets.WebSocketServerProtocol, _path: str = "") -> None:
    await register_client(websocket)
    peer = websocket.remote_address
    peer_label = f"{peer[0]}:{peer[1]}" if peer else "unknown-client"

    try:
        async for message in websocket:
            if message.startswith("__name__:"):
                name = message.split(":", 1)[1].strip() or "anonymous"
                async with clients_lock:
                    client_names[websocket] = name
                print(f"Client registered name '{name}' from {peer_label}")
                await broadcast_message(f"{name} joined the chat")
                continue

            async with clients_lock:
                name = client_names.get(websocket, "anonymous")

            outgoing = f"{name}: {message}"
            print(f"Received: {outgoing}")
            await broadcast_message(outgoing)
    except ConnectionClosed:
        pass
    finally:
        await unregister_client(websocket)


async def start_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    print(f"Starting broadcast server on ws://{host}:{port}")

    server = await websockets.serve(handle_client, host, port)
    print("Server is running. Press Ctrl+C to stop.")

    try:
        await asyncio.Future()
    finally:
        server.close()
        await server.wait_closed()

        async with clients_lock:
            clients = list(connected_clients)
            connected_clients.clear()

        await asyncio.gather(
            *(client.close(code=1001, reason="Server shutting down") for client in clients),
            return_exceptions=True,
        )
