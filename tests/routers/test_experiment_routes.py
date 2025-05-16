# tests/routers/test_experiment_routes.py
import pytest
from fastapi import status

@pytest.fixture
def sample_service(client):
    response = client.post("/api/v1/services", json={"name": "test-service", "active": True})
    return response.json()


@pytest.fixture
def sample_experiment_data(sample_service, client):
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


def test_list_experiments(sample_experiment_data, client):
    # First create an experiment
    client.post(
        f"/api/v1/services/{sample_experiment_data['service_id']}/experiments",
        json=sample_experiment_data
    )

    response = client.get(
        f"/api/v1/services/{sample_experiment_data['service_id']}/experiments"
    )
    assert response.status_code == status.HTTP_200_OK
    experiments = response.json()
    assert len(experiments) > 0
    assert experiments[0]["service_id"] == sample_experiment_data["service_id"]