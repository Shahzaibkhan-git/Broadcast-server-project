from __future__ import annotations

import asyncio

import websockets
from websockets.exceptions import ConnectionClosed


async def receive_messages(websocket: websockets.WebSocketClientProtocol) -> None:
    try:
        async for message in websocket:
            print(f"\n{message}")
    except ConnectionClosed:
        print("Server closed the connection.")


async def send_messages(websocket: websockets.WebSocketClientProtocol, name: str) -> None:
    prompt = f"{name}> " if name else "> "
    while True:
        try:
            text = await asyncio.to_thread(input, prompt)
        except EOFError:
            text = "/quit"

        text = text.strip()
        if not text:
            continue

        if text.lower() in {"/quit", "/exit"}:
            await websocket.close()
            break

        try:
            await websocket.send(text)
        except ConnectionClosed:
            print("Disconnected from server.")
            break


async def run_client(host: str = "127.0.0.1", port: int = 8765, name: str = "anonymous") -> None:
    uri = f"ws://{host}:{port}"
    print(f"Connecting to {uri} ...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected. Type /quit to exit.")
            await websocket.send(f"__name__:{name}")

            receiver = asyncio.create_task(receive_messages(websocket))
            sender = asyncio.create_task(send_messages(websocket, name))

            done, pending = await asyncio.wait(
                {receiver, sender},
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)

            for task in done:
                exc = task.exception()
                if exc:
                    raise exc
    except ConnectionClosed:
        print("Connection closed.")
    except OSError as exc:
        print(f"Could not connect to server: {exc}")
