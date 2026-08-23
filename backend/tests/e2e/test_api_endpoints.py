import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Clean Architecture" in data["message"]

def test_list_chats_api():
    create_res = client.post("/api/chats", json={"title": "List Test Chat", "model": "gemini-3.1-flash-lite"})
    assert create_res.status_code == 200
    created_id = create_res.json()["id"]

    response = client.get("/api/chats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(c["id"] == created_id for c in data)

    client.delete(f"/api/chats/{created_id}")

def test_create_and_delete_chat_api():
    # 1. Create chat
    create_res = client.post("/api/chats", json={"title": "E2E Test Chat", "model": "gemini-3.1-flash-lite"})
    assert create_res.status_code == 200
    chat_data = create_res.json()
    chat_id = chat_data["id"]
    assert chat_data["title"] == "E2E Test Chat"

    # 2. Get messages for newly created chat
    msg_res = client.get(f"/api/chats/{chat_id}/messages")
    assert msg_res.status_code == 200
    assert msg_res.json() == []

    # 3. Delete chat
    del_res = client.delete(f"/api/chats/{chat_id}")
    assert del_res.status_code == 200
    assert del_res.json()["id"] == chat_id

    # 4. Verify 404 on deleting non-existent chat
    del_res_404 = client.delete(f"/api/chats/{chat_id}")
    assert del_res_404.status_code == 404

def test_generate_endpoint_api():
    payload = {
        "prompt": "Hello Jemini!",
        "model": "gemini-3.1-flash-lite"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    content = response.text
    assert "data: {" in content
    assert '"type": "done"' in content
