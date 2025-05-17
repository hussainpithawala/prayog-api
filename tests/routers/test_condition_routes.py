# tests/routers/test_condition_routes.py
import pytest
from fastapi import status

@pytest.fixture
def sample_criterion(client, create_temp_service):
    service = create_temp_service
    experiment = client.post(
        f"/api/v1/services/{service['id']}/experiments",
        json={"name": "test-exp", "active": True, "service_id": service["id"]}
    ).json()
    criterion = client.post(
        f"/api/v1/experiments/{experiment['id']}/criteria",
        json={
            "criterion": {
                "experiment_id": experiment.get('id'),
                "sampling_model": "User",
                "sampling_attribute": "attributes"
            },
            "conditions": []
        }
    ).json()
    return criterion


def test_create_condition(sample_criterion, client, delete_temp_service):
    condition_data = {
        "experiment_id": sample_criterion['experiment_id'],
        "criterion_id": sample_criterion['id'],
        "model": "User",
        "property": "age",
        "value": "30",
        "condition": "gte"
    }
    response = client.post(
        f"/api/v1/criteria/{sample_criterion['id']}/conditions",
        json=condition_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["property"] == "age"


def test_list_conditions(sample_criterion, client, delete_temp_service):
    # First create a condition
    client.post(
        f"/api/v1/criteria/{sample_criterion['id']}/conditions",
        json={
            "experiment_id": sample_criterion['experiment_id'],
            "criterion_id": sample_criterion['id'],
            "model": "User",
            "property": "country",
            "value": "US",
            "condition": "equals"
        }
    )

    response = client.get(f"/api/v1/criteria/{sample_criterion['id']}/conditions")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0