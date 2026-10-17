import pytest
from fastapi.testclient import TestClient

from app_under_test.chat_api import app

pytestmark = [pytest.mark.api, pytest.mark.regression]

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_message():
    response = client.post("/messages", json={"text": "hello", "author": "adarsh"})
    assert response.status_code == 201
    body = response.json()
    assert body["text"] == "hello"
    assert body["author"] == "adarsh"
    assert isinstance(body["id"], int)


@pytest.mark.parametrize(
    "payload",
    [{"text": ""}, {"text": "x" * 501}, {"author": "no text"}],
    ids=["empty_text", "too_long", "missing_text"],
)
def test_invalid_message_is_rejected(payload):
    response = client.post("/messages", json=payload)
    assert response.status_code == 422


def test_get_message_by_id():
    created = client.post("/messages", json={"text": "find me"}).json()
    response = client.get(f"/messages/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_unknown_message_returns_404():
    response = client.get("/messages/999999")
    assert response.status_code == 404


def test_list_respects_limit():
    for i in range(3):
        client.post("/messages", json={"text": f"msg {i}"})
    response = client.get("/messages", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2