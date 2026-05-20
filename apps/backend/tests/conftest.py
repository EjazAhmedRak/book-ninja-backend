import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True, scope="session")
def mock_env():
    """Inject dummy env vars so config.py does not raise KeyError on import."""
    env_vars = {
        "OPENAI_API_KEY": "test-openai-key",
        "TAVILY_API_KEY": "test-tavily-key",
        "HARDCOVER_API_KEY": "test-hardcover-key",
        "MONGO_URI": "mongodb://localhost:27017/book_ninja_test",
        "LANGSMITH_API_KEY": "test-ls-key",
        "GOOGLE_CLIENT_ID": "test-client-id",
        "LANGCHAIN_TRACING_V2": "false",
        "LANGCHAIN_PROJECT": "book-ninja-test",
    }
    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
def mock_google_user():
    from api.middleware.auth import GoogleUser
    return GoogleUser(sub="user123", email="test@example.com")


@pytest.fixture
def test_client(mock_google_user):
    from main import app
    from api.middleware.auth import validate_google_token
    from fastapi.testclient import TestClient
    app.dependency_overrides[validate_google_token] = lambda: mock_google_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
