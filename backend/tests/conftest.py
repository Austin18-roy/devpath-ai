import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client():
    """Provides a FastAPI TestClient instance for API tests."""
    with TestClient(app) as test_client:
        yield test_client

