from fastapi.testclient import TestClient
from library_management.app import app
import pytest 

@pytest.fixture
def client():
    yield TestClient(app)