from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException


def test_auth_me_returns_authenticated_user(test_client):
    with patch("api.routes.auth.save_user", new_callable=AsyncMock):
        res = test_client.get("/auth/me")

    assert res.status_code == 200
    assert res.json() == {"sub": "user123", "email": "test@example.com"}


def test_cors_allows_vite_frontend_preflight(test_client):
    res = test_client.options(
        "/auth/me",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )

    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "authorization" in res.headers["access-control-allow-headers"].lower()


def test_auth_me_saves_authenticated_user(test_client):
    with patch("api.routes.auth.save_user", new_callable=AsyncMock) as mock_save_user:
        res = test_client.get("/auth/me")

    assert res.status_code == 200
    mock_save_user.assert_awaited_once()
    saved_user = mock_save_user.await_args.args[0]
    assert saved_user.email == "test@example.com"
    assert saved_user.google_id == "user123"


@pytest.mark.asyncio
async def test_auth_me_returns_503_when_user_persistence_fails(mock_google_user):
    from api.routes.auth import auth_me

    with patch("api.routes.auth.save_user", new_callable=AsyncMock) as mock_save_user:
        mock_save_user.side_effect = RuntimeError("mongo unavailable")

        with pytest.raises(HTTPException) as exc_info:
            await auth_me(user=mock_google_user)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Unable to create or update user session."
