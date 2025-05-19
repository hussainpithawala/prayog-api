# tests/routers/test_sample_routes.py
import pytest
from fastapi import status


def test_create_sample(create_temp_experiment, client):
    sample_data = {
        "experiment_id": create_temp_experiment['id'],
        "sampled_entity": "user123",
        "sampled_value": "US",
        "allocated_bucket": "test-bucket"
    }
    response = client.post(
        f"/api/v1/experiments/{create_temp_experiment['id']}/samples",
        json=sample_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["sampled_entity"] == "user123"


def test_list_samples(create_temp_experiment, client):
    # First create a sample
    client.post(
        f"/api/v1/experiments/{create_temp_experiment['id']}/samples",
        json={
            "experiment_id": create_temp_experiment['id'],
            "sampled_entity": "user456",
            "sampled_value": "UK",
            "allocated_bucket": "test-bucket"
        }
    )

    response = client.get(f"/api/v1/experiments/{create_temp_experiment['id']}/samples")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
