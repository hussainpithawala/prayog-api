# tests/routers/test_experiment_routes.py
import pytest
from fastapi import status

@pytest.fixture
def sample_experiment_data(client, create_temp_service):
    sample_service = create_temp_service
    return {
        "name": "test-experiment",
        "active": True,
        "service_id": sample_service["id"]
    }


def test_create_experiment(sample_experiment_data, client):
    response = client.post(
        f"/api/v1/services/{sample_experiment_data['service_id']}/experiments",
        json=sample_experiment_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == sample_experiment_data["name"]
    assert data["service_id"] == sample_experiment_data["service_id"]


def test_list_experiments(client, sample_create_bulk_experiments):
    test_service, test_experiments = sample_create_bulk_experiments
    """
    Test the paginated list experiments API endpoint.

    - Ensures pagination works correctly.
    - Verifies next_page_token handling.
    """
    limit = 3  # Number of records per page
    active_only = True  # Only fetch active experiments

    # Initialize variables for pagination
    all_experiments = []
    next_page_token = None

    service_id = test_service['id']

    while True:
        # Prepare query parameters for the request
        params = {
            "limit": limit,
            "active_only": active_only,
        }
        if next_page_token:
            params["page_token"] = next_page_token

        # Send GET request to the paginated endpoint
        response = client.get(f"/api/v1/services/{service_id}/experiments", params=params)
        assert response.status_code == status.HTTP_200_OK

        # Parse the response JSON
        data = response.json()
        current_experiments = data["experiments"]
        next_page_token = data.get("next_page_token")

        # Validate the experiments returned on this page
        assert isinstance(current_experiments, list)
        assert len(current_experiments) <= limit

        # Check that all experiments are active (active_only=True)
        for experiment in current_experiments:
            assert experiment["active"] is True

        # Accumulate the experiments
        all_experiments.extend(current_experiments)

        # Exit the loop if there's no next page
        if not next_page_token:
            break

    # Verify that the correct number of results are returned
    expected_experiments = [
        experiment for experiment in test_experiments if experiment["active"]
    ]
    assert len(all_experiments) == len(expected_experiments)

