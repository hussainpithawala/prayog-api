# tests/routers/test_criterion_routes.py
from fastapi import status


def test_create_criterion_with_conditions(create_temp_experiment, client):
    criterion_data = {
        "experiment_id": create_temp_experiment['id'],
        "sampling_model": "User",
        "sampling_attribute": "attributes"
    }
    conditions = [
        {
            "experiment_id": create_temp_experiment['id'],
            "model": "User",
            "property": "country",
            "value": "US",
            "condition": "equals"
        }
    ]

    response = client.post(
        f"/api/v1/experiments/{create_temp_experiment['id']}/criteria",
        json={
            "experiment_id": create_temp_experiment['id'],
            "criterion": criterion_data,
            "conditions": conditions
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["sampling_model"] == "User"
    assert len(data["conditions"]) == 1


def test_list_criterions(client, sample_create_bulk_criterions):
    test_experiment, test_criterions = sample_create_bulk_criterions
    """
    Test the paginated list criterions API endpoint.

    - Ensures pagination works correctly.
    - Verifies next_page_token handling.
    """
    limit = 3  # Number of records per page
    active_only = True  # Only fetch active criterions

    # Initialize variables for pagination
    all_criterions = []
    next_page_token = None

    experiment_id = test_experiment['id']

    while True:
        # Prepare query parameters for the request
        params = {
            "limit": limit
        }
        if next_page_token:
            params["page_token"] = next_page_token

        # Send GET request to the paginated endpoint
        response = client.get(f"/api/v1/experiments/{experiment_id}/criteria", params=params)
        assert response.status_code == status.HTTP_200_OK

        # Parse the response JSON
        data = response.json()
        current_criterions = data["criterions"]
        next_page_token = data.get("next_page_token")

        # Validate the criterions returned on this page
        assert isinstance(current_criterions, list)
        assert len(current_criterions) <= limit

        # Accumulate the criterions
        all_criterions.extend(current_criterions)

        # Exit the loop if there's no next page
        if not next_page_token:
            break

    # Verify that the correct number of results are returned
    assert len(all_criterions) == len(test_criterions)
