"""
Integration tests for the FastAPI endpoints.

These tests require a running PostgreSQL+pgvector instance.
Run: docker compose up -d
Then: cd backend && pytest tests/test_api.py -v
"""

import os
import sys

import pytest

# Skip all tests in this module if database is not available
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_DB_TESTS", "1") == "1",
    reason="Set SKIP_DB_TESTS=0 and ensure DB is running to run integration tests",
)

pytest_plugins = []


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    from httpx import ASGITransport, AsyncClient
    from main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.anyio
async def test_list_documents_empty(client):
    resp = await client.get("/api/documents")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.anyio
async def test_create_conversation(client):
    resp = await client.post("/api/conversations", json={"title": "Test Conversation"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Test Conversation"
    assert "id" in data


@pytest.mark.anyio
async def test_list_conversations(client):
    resp = await client.get("/api/conversations")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.anyio
async def test_upload_invalid_file_type(client):
    resp = await client.post(
        "/api/documents",
        files={"file": ("test.txt", b"hello world", "text/plain")},
    )
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_conversation_not_found(client):
    resp = await client.get("/api/conversations/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_chat_conversation_not_found(client):
    resp = await client.post(
        "/api/chat",
        json={
            "conversation_id": "00000000-0000-0000-0000-000000000000",
            "message": "hello",
        },
    )
    assert resp.status_code == 404
