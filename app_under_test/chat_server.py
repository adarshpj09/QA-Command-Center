import json
import threading

from websockets.exceptions import ConnectionClosed
from websockets.sync.server import serve

CLIENTS = set()
LOCK = threading.Lock()
MAX_TEXT_LENGTH = 500


def send_json(connection, payload):
    connection.send(json.dumps(payload))


def broadcast(payload):
    with LOCK:
        targets = list(CLIENTS)
    for client in targets:
        try:
            send_json(client, payload)
        except ConnectionClosed:
            pass


def handler(connection):
    with LOCK:
        CLIENTS.add(connection)
    try:
        for raw in connection:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                send_json(connection, {"type": "error", "message": "invalid json"})
                continue

            if not isinstance(data, dict):
                send_json(connection, {"type": "error", "message": "invalid message"})
                continue

            kind = data.get("type")
            if kind == "ping":
                send_json(connection, {"type": "pong"})
            elif kind == "chat":
                text = data.get("text")
                if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT_LENGTH:
                    send_json(connection, {"type": "error", "message": "invalid text"})
                else:
                    broadcast({"type": "chat", "text": text})
            else:
                send_json(connection, {"type": "error", "message": "unknown type"})
    except ConnectionClosed:
        pass
    finally:
        with LOCK:
            CLIENTS.discard(connection)


def start_server(host="127.0.0.1", port=8765):
    server = serve(handler, host, port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


if __name__ == "__main__":
    start_server()
    print("Chat server running on ws://127.0.0.1:8765")
    threading.Event().wait()