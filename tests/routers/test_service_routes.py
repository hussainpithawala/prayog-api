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

    service_id = data['id']
    response = client.delete(f"/api/v1/services/{service_id}")
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"message": f"service {service_id} deleted successfully"}


def test_list_services(client, sample_create_bulk_services, sample_delete_bulk_services):
    """
        Test the paginated list services API endpoint.

        - Ensures pagination works correctly.
        - Verifies next_page_token handling.
        """
    limit = 3  # Number of records per page
    active_only = True  # Only fetch active services

    # Initialize variables for pagination
    all_services = []
    next_page_token = None

    while True:
        # Prepare query parameters for the request
        params = {
            "limit": limit,
            "active_only": active_only,
        }
        if next_page_token:
            params["page_token"] = next_page_token

        # Send GET request to the paginated endpoint
        response = client.get("/api/v1/services", params=params)
        assert response.status_code == status.HTTP_200_OK

        # Parse the response JSON
        data = response.json()
        current_services = data["services"]
        next_page_token = data.get("next_page_token")

        # Validate the services returned on this page
        assert isinstance(current_services, list)
        assert len(current_services) <= limit

        # Check that all services are active (active_only=True)
        for service in current_services:
            assert service["active"] is True

        # Accumulate the services
        all_services.extend(current_services)

        # Exit the loop if there's no next page
        if not next_page_token:
            break

    # Verify that the correct number of results are returned
    expected_services = [
        service for service in sample_create_bulk_services if service["active"]
    ]
    assert len(all_services) == len(expected_services)


def test_get_service(client, create_temp_service, delete_temp_service):
    # First create a service to get
    service_id = create_temp_service['id']
    response = client.get(f"/api/v1/services/{service_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == service_id


def test_get_nonexistent_service(client):
    fake_id = uuid4()
    response = client.get(f"/api/v1/services/{fake_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
