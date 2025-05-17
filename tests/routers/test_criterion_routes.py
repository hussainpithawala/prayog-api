# tests/routers/test_criterion_routes.py
from fastapi import status


def test_create_criterion_with_conditions(sample_experiment, client, delete_temp_service):
    criterion_data = {
        "experiment_id": sample_experiment['id'],
        "sampling_model": "User",
        "sampling_attribute": "attributes"
    }
    conditions = [
        {
            "experiment_id": sample_experiment['id'],
            "model": "User",
            "property": "country",
            "value": "US",
            "condition": "equals"
        }
    ]

    response = client.post(
        f"/api/v1/experiments/{sample_experiment['id']}/criteria",
        json={
            "experiment_id": sample_experiment['id'],
            "criterion": criterion_data,
            "conditions": conditions
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["sampling_model"] == "User"
    assert len(data["conditions"]) == 1
