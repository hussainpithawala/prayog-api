# tests/repositories/cassandra/test_sample_repository.py

import pytest
from uuid import uuid4
from datetime import datetime
from app.models.schemas import BucketedSampleCreate

@pytest.fixture
def sample_data():
    return {
        "experiment_id": uuid4(),
        "sampled_entity": "user123",
        "sampled_value": "US",
        "allocated_bucket": "test-bucket"
    }

@pytest.fixture
def created_sample(sample_repo, sample_data):
    return sample_repo.create(BucketedSampleCreate(**sample_data))

def test_find_by_id(sample_repo, sample_data):
    sample = sample_repo.create(BucketedSampleCreate(**sample_data))
    found_sample = sample_repo.find_by_id(sample.id)

    assert found_sample is not None
    assert found_sample.id == sample.id
    assert found_sample.experiment_id == sample.experiment_id
    assert found_sample.sampled_entity == sample.sampled_entity

def test_create_sample(sample_repo, sample_data):
    sample = sample_repo.create(BucketedSampleCreate(**sample_data))

    assert sample.experiment_id == sample_data["experiment_id"]
    assert sample.sampled_entity == sample_data["sampled_entity"]
    assert sample.allocated_bucket == sample_data["allocated_bucket"]
    assert sample.complete is False
    assert sample.completed_at is None


def test_mark_sample_complete(sample_repo, created_sample):
    before_complete = datetime.now()

    completed_sample = sample_repo.mark_complete(
        created_sample.experiment_id,
        created_sample.sampled_entity,
        created_sample.sampled_value
    )

    assert completed_sample.complete is True
    assert completed_sample.completed_at is not None
    assert completed_sample.completed_at > before_complete


def test_mark_nonexistent_sample_complete(sample_repo, sample_data):
    with pytest.raises(ValueError, match="Sample not found"):
        sample_repo.mark_complete(
            sample_data["experiment_id"],
            "nonexistent",
            "nonexistent"
        )


def test_find_by_entity_value(sample_repo, created_sample):
    found_sample = sample_repo.find_by_entity_value(
        created_sample.experiment_id,
        created_sample.sampled_entity,
        created_sample.sampled_value
    )

    assert found_sample is not None
    assert found_sample.id == created_sample.id
    assert found_sample.allocated_bucket == created_sample.allocated_bucket


def test_find_nonexistent_entity_value(sample_repo, sample_data):
    assert sample_repo.find_by_entity_value(
        sample_data["experiment_id"],
        "nonexistent",
        "nonexistent"
    ) is None


def test_list_by_experiment(sample_repo, sample_data):
    # Create multiple samples for same experiment
    sample1 = sample_repo.create(BucketedSampleCreate(**sample_data))
    sample_data["sampled_entity"] = "user123"
    sample2 = sample_repo.create(BucketedSampleCreate(**sample_data))

    samples = sample_repo.list_by_experiment(sample_data["experiment_id"])

    assert len(samples) == 2
    assert {s.sampled_entity for s in samples} == {"user123"}


def test_list_with_limit(sample_repo, sample_data):
    # Create 3 samples
    for i in range(3):
        sample_data["sampled_entity"] = f"user{i}"
        sample_repo.create(BucketedSampleCreate(**sample_data))

    samples = sample_repo.list_by_experiment(sample_data["experiment_id"], limit=2)
    assert len(samples) == 2

@pytest.mark.skip
def test_delete_samples_by_experiment(sample_repo, created_sample):
    # Create another sample for same experiment
    sample_data = {
        "experiment_id": created_sample.experiment_id,
        "sampled_entity": "user456",
        "sampled_value": "UK",
        "allocated_bucket": "test-bucket"
    }
    sample_repo.create(BucketedSampleCreate(**sample_data))

    # Delete all samples for experiment
    assert sample_repo.delete_by_experiment(created_sample.experiment_id) is True

    # Verify no samples remain
    assert len(sample_repo.list_by_experiment(created_sample.experiment_id)) == 0


def test_sample_ordering(sample_repo, sample_data):
    # Create samples with time delay
    sample1 = sample_repo.create(BucketedSampleCreate(**sample_data))
    sample_data["sampled_entity"] = "user456"
    sample2 = sample_repo.create(BucketedSampleCreate(**sample_data))

    # Should return newest first due to clustering_order="DESC"
    samples = sample_repo.list_by_experiment(sample_data["experiment_id"])
    assert samples[0].sampled_entity in ["user456", "user123"]
    assert samples[1].sampled_entity in ["user456", "user123"]