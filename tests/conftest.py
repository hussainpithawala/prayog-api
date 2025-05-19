# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from starlette import status

from app.main import app
from cassandra.cluster import Cluster
from cassandra.cqlengine import connection


@pytest.fixture(scope="session")
def cassandra_session():
    """Setup Cassandra test cluster"""
    cluster = connection.setup(['127.0.0.1'], default_keyspace='test_experimentation')
    yield cluster
    connection.unregister_connection('default')


@pytest.fixture(scope="session")
def client(cassandra_session):
    """Override app dependencies with test session"""
    # Initialize your app with test configuration
    from app.dependencies import get_service_repository
    from app.repositories.cassandra.service_repository import ServiceRepository

    # Override dependencies to use test session
    def get_test_service_repo():
        return ServiceRepository()

    app.dependency_overrides[get_service_repository] = get_test_service_repo

    yield TestClient(app)

    # Clear overrides after tests
    app.dependency_overrides.clear()


@pytest.fixture
def create_temp_experiment(client, create_temp_service):
    test_service = create_temp_service

    test_experiment = client.post(
        f"/api/v1/services/{test_service['id']}/experiments",
        json={"name": "test-exp-buzz", "active": True, "service_id": test_service["id"]}
    ).json()
    yield test_experiment
    response = client.delete(f"/api/v1/services/{test_service['id']}/experiments/{test_experiment['id']}")
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"message": f"experiment {test_experiment['id']} deleted successfully"}


@pytest.fixture
def create_temp_service(client):
    create_response = client.post("/api/v1/services", json={"name": "temp-service", "active": True})
    temp_service = create_response.json()
    yield temp_service
    service_id = temp_service['id']
    response = client.delete(f"/api/v1/services/{service_id}")
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"message": f"service {service_id} deleted successfully"}

@pytest.fixture
def sample_create_bulk_services(client):
    yield [client.post("/api/v1/services", json={"name": f"test-service-{index}", "active": True}).json() for index in
           range(1, 10)]

@pytest.fixture
def sample_create_bulk_experiments(client, create_temp_service):
    test_service = create_temp_service
    test_experiments = [client.post(
        f"/api/v1/services/{test_service['id']}/experiments",
        json={"name": f"test-exp-{index}", "active": True, "service_id": test_service["id"]}
    ).json() for index in range(1, 10)]
    yield test_service, test_experiments

    for test_experiment in test_experiments:
        response = client.delete(f"/api/v1/services/{test_service['id']}/experiments/{test_experiment['id']}")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {"message": f"experiment {test_experiment['id']} deleted successfully"}


@pytest.fixture
def sample_delete_bulk_services(client, sample_create_bulk_services):
    yield
    for service in sample_create_bulk_services:
        service_id = service['id']
        response = client.delete(f"/api/v1/services/{service_id}")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {"message": f"service {service_id} deleted successfully"}

@pytest.fixture
def sample_create_bulk_criterions(client, create_temp_experiment):
    test_experiment = create_temp_experiment
    test_criterions = [client.post(
        f"/api/v1/experiments/{test_experiment['id']}/criteria",
        json={
            "experiment_id": test_experiment['id'],
            "criterion": {
                "experiment_id": test_experiment['id'],
                "sampling_model": f"test-model-{index}",
                "sampling_attribute": "attributes"
            },
            "conditions": [{
                "experiment_id": test_experiment['id'],
                "model": f"test-model-{index}",
                "property": "country",
                "value": "US",
                "condition": "equals"
            }]
        }
    ).json() for index in range(1, 10)]
    yield test_experiment, test_criterions

    for test_criterion in test_criterions:
        response = client.delete(f"/api/v1/experiments/{test_experiment['id']}/criteria/{test_criterion['id']}")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {"message": f"criterion {test_criterion['id']} deleted successfully"}

@pytest.fixture
def clean_tables(cassandra_session):
    """Clean tables between tests"""
    yield
    # Truncate all tables between tests
    tables = cassandra_session.execute(
        "SELECT table_name FROM system_schema.tables WHERE keyspace_name = 'test_experimentation'"
    )
    for table in tables:
        cassandra_session.execute(f"TRUNCATE {table.table_name}")
