import pytest
import requests
from jsonschema import validate

BASE_URL = "https://jsonplaceholder.typicode.com"
pytestmark = [pytest.mark.api, pytest.mark.regression]

POST_SCHEMA = {
    "type": "object",
    "required": ["userId", "id", "title", "body"],
    "properties": {
        "userId": {"type": "integer"},
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "body": {"type": "string"},
    },
}

@pytest.mark.smoke
def test_get_all_posts():
    response = requests.get(f"{BASE_URL}/posts", timeout=10)
    assert response.status_code == 200
    assert len(response.json()) == 100


@pytest.mark.parametrize("post_id", [1, 2, 50, 100])
def test_get_single_post_matches_schema(post_id):
    response = requests.get(f"{BASE_URL}/posts/{post_id}", timeout=10)
    assert response.status_code == 200
    body = response.json()
    validate(instance=body, schema=POST_SCHEMA)
    assert body["id"] == post_id


def test_get_nonexistent_post_returns_404():
    response = requests.get(f"{BASE_URL}/posts/99999", timeout=10)
    assert response.status_code == 404


def test_create_post():
    payload = {"title": "QA test", "body": "created by pytest", "userId": 1}
    response = requests.post(f"{BASE_URL}/posts", json=payload, timeout=10)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == payload["title"]
    assert "id" in body


def test_response_time_under_two_seconds():
    response = requests.get(f"{BASE_URL}/posts/1", timeout=10)
    assert response.elapsed.total_seconds() < 2