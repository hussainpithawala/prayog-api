# tests/test_buckets_repository.py
import uuid

import pytest
from uuid import UUID
from app.models.schemas import ExperimentBucket, ExperimentBucketCreate


def test_create_bucket(bucket_repo, sample_bucket):
    created_bucket = bucket_repo.create(
        sample_bucket
    )

    assert isinstance(created_bucket, ExperimentBucket)
    assert created_bucket.bucket_name == sample_bucket.bucket_name
    assert created_bucket.percentage_distribution == sample_bucket.percentage_distribution


def test_find_bucket_by_name(bucket_repo, sample_bucket):
    created_bucket = bucket_repo.create(
        sample_bucket
    )

    found_bucket = bucket_repo.find_by_experiment_and_name(
        created_bucket.experiment_id,
        created_bucket.bucket_name
    )

    assert found_bucket is not None
    assert found_bucket.bucket_name == sample_bucket.bucket_name


def test_update_bucket_distribution(bucket_repo, sample_bucket):
    created_bucket = bucket_repo.create(
        sample_bucket
    )

    updated_bucket = bucket_repo.update_distribution(
        created_bucket.experiment_id,
        sample_bucket.bucket_name,
        75
    )

    assert updated_bucket.percentage_distribution == 75


def test_list_buckets(bucket_repo, sample_bucket):
    initial_count = len(bucket_repo.list_by_experiment(uuid.uuid4()))
    created_bucket = bucket_repo.create(sample_bucket)

    buckets = bucket_repo.list_by_experiment(created_bucket.experiment_id)
    assert len(buckets) == initial_count + 1