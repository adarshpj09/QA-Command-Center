import threading

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Chat API under test", version="1.0.0")

MESSAGES = []
LOCK = threading.Lock()


class MessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    author: str = Field(default="anonymous", min_length=1, max_length=50)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/messages", status_code=201)
def create_message(message: MessageIn):
    with LOCK:
        item = {
            "id": len(MESSAGES) + 1,
            "text": message.text,
            "author": message.author,
        }
        MESSAGES.append(item)
    return item


@app.get("/messages")
def list_messages(limit: int = Query(50, ge=1, le=200)):
    with LOCK:
        return MESSAGES[-limit:]


@app.get("/messages/{message_id}")
def get_message(message_id: int):
    with LOCK:
        if message_id < 1 or message_id > len(MESSAGES):
            raise HTTPException(status_code=404, detail="message not found")
        return MESSAGES[message_id - 1]