# tests/routers/test_service_routes.py
import pytest
from fastapi import status
from uuid import uuid4

@pytest.fixture
def sample_service_data():
    return {"name": "test-service", "active": True}


def test_create_service(sample_service_data, client):
    response = client.post("/api/v1/services", json=sample_service_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == sample_service_data["name"]
    assert "id" in data


def test_list_services(client):
    response = client.get("/api/v1/services")
    assert response.status_code == status.HTTP_200_OK
    services = response.json()
    assert isinstance(services, list)


def test_get_service(client):
    # First create a service to get
    create_response = client.post("/api/v1/services", json={"name": "temp-service", "active": True})
    service_id = create_response.json()["id"]

    response = client.get(f"/api/v1/services/{service_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == service_id


def test_get_nonexistent_service(client):
    fake_id = uuid4()
    response = client.get(f"/api/v1/services/{fake_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND