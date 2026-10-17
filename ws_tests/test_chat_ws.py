import json
import time

import pytest
from websockets.sync.client import connect

pytestmark = [pytest.mark.websocket, pytest.mark.regression]


def ping(ws):
    ws.send(json.dumps({"type": "ping"}))
    return json.loads(ws.recv(timeout=5))


def connect_ready(url):
    """Connect and confirm the server is handling this client."""
    ws = connect(url)
    assert ping(ws) == {"type": "pong"}
    return ws


@pytest.mark.smoke
def test_connect_and_ping(ws_url):
    with connect(ws_url) as ws:
        assert ping(ws) == {"type": "pong"}


def test_chat_message_reaches_all_clients(ws_url):
    with connect_ready(ws_url) as sender, connect_ready(ws_url) as receiver:
        sender.send(json.dumps({"type": "chat", "text": "hello team"}))
        expected = {"type": "chat", "text": "hello team"}
        assert json.loads(sender.recv(timeout=5)) == expected
        assert json.loads(receiver.recv(timeout=5)) == expected


def test_invalid_json_returns_error(ws_url):
    with connect(ws_url) as ws:
        ws.send("this is not json")
        reply = json.loads(ws.recv(timeout=5))
        assert reply == {"type": "error", "message": "invalid json"}


def test_unknown_type_returns_error(ws_url):
    with connect(ws_url) as ws:
        ws.send(json.dumps({"type": "dance"}))
        reply = json.loads(ws.recv(timeout=5))
        assert reply == {"type": "error", "message": "unknown type"}


@pytest.mark.parametrize(
    "bad_text",
    ["", 123, None, "x" * 501],
    ids=["empty", "number", "null", "too_long"],
)
def test_invalid_chat_text_is_rejected(ws_url, bad_text):
    with connect(ws_url) as ws:
        ws.send(json.dumps({"type": "chat", "text": bad_text}))
        reply = json.loads(ws.recv(timeout=5))
        assert reply == {"type": "error", "message": "invalid text"}


def test_round_trip_latency_is_low(ws_url):
    with connect_ready(ws_url) as ws:
        timings = []
        for _ in range(20):
            start = time.perf_counter()
            assert ping(ws) == {"type": "pong"}
            timings.append((time.perf_counter() - start) * 1000)
        average = sum(timings) / len(timings)
        print(f"average latency: {average:.2f} ms, max: {max(timings):.2f} ms")
        assert average < 100


def test_connection_stays_stable_over_many_messages(ws_url):
    with connect_ready(ws_url) as ws:
        for _ in range(100):
            assert ping(ws) == {"type": "pong"}


def test_client_can_reconnect_after_disconnect(ws_url):
    first = connect_ready(ws_url)
    first.close()
    with connect_ready(ws_url) as second:
        assert ping(second) == {"type": "pong"}