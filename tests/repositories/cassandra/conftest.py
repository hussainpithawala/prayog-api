# tests/repositories/cassandra/conftest.py
import pytest
from uuid import uuid4
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table, drop_table

from app.repositories.cassandra.service_repository import ServiceRepository
from app.repositories.cassandra.experiment_repository import ExperimentRepository
from app.repositories.cassandra.bucket_repository import BucketRepository
from app.repositories.cassandra.bucketed_sample_repository import BucketedSampleRepository

from app.repositories.cassandra.service_repository import ServiceModel
from app.repositories.cassandra.experiment_repository import ExperimentModel
from app.repositories.cassandra.bucket_repository import ExperimentBucketModel
from app.repositories.cassandra.bucketed_sample_repository import BucketedSampleModel
from app.repositories.cassandra.experiment_sampling_condition_repository import (
    ExperimentSamplingConditionModel,
    ExperimentSamplingConditionRepository
)
from app.repositories.cassandra.experiment_sampling_criterion_repository import (
    ExperimentSamplingCriterionModel,
    ExperimentSamplingCriterionRepository
)

from app.models.schemas import (
    ServiceCreate,
    ExperimentCreate,
    ExperimentBucketCreate,
    ExperimentSamplingCriterionCreate,
    BucketedSampleCreate, ExperimentSamplingConditionCreate
)

@pytest.fixture(scope="module")
def cassandra_session():
    """Setup Cassandra test cluster"""
    cluster = connection.setup(['127.0.0.1'], default_keyspace='test_experimentation')
    yield cluster
    connection.unregister_connection('default')

@pytest.fixture
def service_repo(cassandra_session):
    sync_table(ServiceModel)
    repo = ServiceRepository()
    yield repo
    drop_table(ServiceModel)

@pytest.fixture
def experiment_repo(cassandra_session):
    sync_table(ExperimentModel)
    repo = ExperimentRepository()
    yield repo
    drop_table(ExperimentModel)

@pytest.fixture
def bucket_repo(cassandra_session):
    sync_table(ExperimentBucketModel)
    repo = BucketRepository()
    yield repo
    drop_table(ExperimentBucketModel)

@pytest.fixture
def sample_repo(cassandra_session):
    sync_table(BucketedSampleModel)
    repo = BucketedSampleRepository()
    yield repo
    drop_table(BucketedSampleModel)

@pytest.fixture
def sample_service():
    return ServiceCreate(
        name="test-service",
        active=True
    )

@pytest.fixture
def sample_experiment():
    return ExperimentCreate(
        name="test-experiment",
        service_id=uuid4(),
        active=True
    )

@pytest.fixture
def sample_bucket():
    return ExperimentBucketCreate(
        experiment_id=uuid4(),
        bucket_name="test-bucket",
        percentage_distribution=50
    )

@pytest.fixture
def sample_sampling_criterion():
    return ExperimentSamplingCriterionCreate(
        experiment_id=uuid4(),
        sampling_model="User",
        sampling_attribute="country",
        conditions=[{"property": "country", "value": "US", "condition": "equals"}]
    )

@pytest.fixture
def sample_bucketed_sample():
    return BucketedSampleCreate(
        experiment_id=uuid4(),
        sampled_entity="user123",
        sampled_value="US",
        allocated_bucket="test-bucket"
    )

@pytest.fixture
def condition_repo(cassandra_session):
    sync_table(ExperimentSamplingConditionModel)
    repo = ExperimentSamplingConditionRepository()
    yield repo
    drop_table(ExperimentSamplingConditionModel)

@pytest.fixture
def criterion_repo(cassandra_session, condition_repo):
    sync_table(ExperimentSamplingCriterionModel)
    repo = ExperimentSamplingCriterionRepository(condition_repo=condition_repo)
    yield repo
    drop_table(ExperimentSamplingCriterionModel)

@pytest.fixture
def sample_condition():
    return ExperimentSamplingConditionCreate(
        criterion_id=uuid4(),
        experiment_id=uuid4(),
        model="User",
        property="country",
        value="US",
        condition="equals"
    )

@pytest.fixture
def sample_criterion():
    return ExperimentSamplingCriterionCreate(
        experiment_id=uuid4(),
        sampling_model="User",
        sampling_attribute="attributes"
    )
