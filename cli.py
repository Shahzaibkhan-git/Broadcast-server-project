import argparse
import asyncio

from client import run_client
from server import start_server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="broadcast-server",
        description="Simple WebSocket broadcast server and client",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start the broadcast server")
    start_parser.add_argument("--host", default="127.0.0.1", help="Host to bind server")
    start_parser.add_argument("--port", type=int, default=8765, help="Port to bind server")

    connect_parser = subparsers.add_parser("connect", help="Connect as a client")
    connect_parser.add_argument("--host", default="127.0.0.1", help="Server host")
    connect_parser.add_argument("--port", type=int, default=8765, help="Server port")
    connect_parser.add_argument("--name", default="anonymous", help="Display name")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "start":
            asyncio.run(start_server(host=args.host, port=args.port))
        elif args.command == "connect":
            asyncio.run(run_client(host=args.host, port=args.port, name=args.name))
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
