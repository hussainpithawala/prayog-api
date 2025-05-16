# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
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
def clean_tables(cassandra_session):
    """Clean tables between tests"""
    yield
    # Truncate all tables between tests
    tables = cassandra_session.execute(
        "SELECT table_name FROM system_schema.tables WHERE keyspace_name = 'test_experimentation'"
    )
    for table in tables:
        cassandra_session.execute(f"TRUNCATE {table.table_name}")