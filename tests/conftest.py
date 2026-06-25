import pytest
from fastapi.testclient import TestClient

from library_management.app import app


@pytest.fixture
def client():
    return TestClient(app)
