# tests/routers/test_bucket_routes.py
from fastapi import status


def test_create_bucket(create_temp_experiment, client):
    bucket_data = {
        "experiment_id": create_temp_experiment['id'],
        "bucket_name": "test-bucket",
        "percentage_distribution": 50
    }
    response = client.post(
        f"/api/v1/experiments/{create_temp_experiment['id']}/buckets",
        json=bucket_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["bucket_name"] == "test-bucket"


def test_list_buckets(create_temp_experiment, client):
    # First create a bucket
    client.post(
        f"/api/v1/experiments/{create_temp_experiment['id']}/buckets",
        json={"experiment_id": create_temp_experiment['id'], "bucket_name": "test-bucket", "percentage_distribution": 50}
    )

    response = client.get(f"/api/v1/experiments/{create_temp_experiment['id']}/buckets")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
