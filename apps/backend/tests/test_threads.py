from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone
from models.thread import ThreadRecord


def _mock_threads():
    return [
        ThreadRecord(
            thread_id=f"user123_thread{i}",
            preview=f"Find me a book about topic {i}",
            timestamp=datetime.now(timezone.utc),
        )
        for i in range(3)
    ]


def test_latest_threads_returns_200(test_client):
    with patch("api.routes.threads.get_latest_threads", new_callable=AsyncMock,
               return_value=_mock_threads()):
        res = test_client.get("/latestThreads")

    assert res.status_code == 200
    body = res.json()
    assert "threads" in body
    assert len(body["threads"]) == 3


def test_latest_threads_structure(test_client):
    with patch("api.routes.threads.get_latest_threads", new_callable=AsyncMock,
               return_value=_mock_threads()):
        res = test_client.get("/latestThreads")

    thread = res.json()["threads"][0]
    assert "thread_id" in thread
    assert "preview" in thread
    assert "timestamp" in thread


def test_latest_threads_empty(test_client):
    with patch("api.routes.threads.get_latest_threads", new_callable=AsyncMock, return_value=[]):
        res = test_client.get("/latestThreads")

    assert res.status_code == 200
    assert res.json()["threads"] == []
