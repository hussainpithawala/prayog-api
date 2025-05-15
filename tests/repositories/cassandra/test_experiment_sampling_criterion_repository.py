# tests/repositories/cassandra/test_experiment_sampling_criterion_repository.py
import pytest
from uuid import uuid4
from app.models.schemas import (
    ExperimentSamplingConditionCreate
)


def test_create_criterion(criterion_repo, sample_criterion):
    created = criterion_repo.create(sample_criterion)
    assert created.id is not None
    assert created.sampling_model == sample_criterion.sampling_model
    assert len(created.conditions) == 0


def test_create_with_conditions(criterion_repo, sample_criterion):
    conditions = [
        ExperimentSamplingConditionCreate(
            criterion_id=uuid4(),  # Will be overwritten
            experiment_id=sample_criterion.experiment_id,
            model="User",
            property="country",
            value="US",
            condition="equals"
        ),
        ExperimentSamplingConditionCreate(
            criterion_id=uuid4(),  # Will be overwritten
            experiment_id=sample_criterion.experiment_id,
            model="User",
            property="age",
            value="30",
            condition="gte"
        )
    ]

    created = criterion_repo.create_with_conditions(sample_criterion, conditions)
    assert len(created.conditions) == 2
    assert all(c.id is not None for c in created.conditions)


def test_find_by_id_with_conditions(criterion_repo, sample_criterion):
    # Create criterion with conditions
    conditions = [
        ExperimentSamplingConditionCreate(
            experiment_id=sample_criterion.experiment_id,
            criterion_id=sample_criterion.id,
            model="User",
            property="country",
            value="US",
            condition="equals"
        )
    ]
    created = criterion_repo.create_with_conditions(sample_criterion, conditions)

    # Retrieve it
    found = criterion_repo.find_by_id(created.id)
    assert found is not None
    assert len(found.conditions) == 1
    assert found.conditions[0].property == "country"


def test_delete_criterion_with_conditions(criterion_repo, sample_criterion):
    # Create criterion with conditions
    conditions = [
        ExperimentSamplingConditionCreate(
            experiment_id=sample_criterion.experiment_id,
            criterion_id=sample_criterion.id,
            model="User",
            property="country",
            value="US",
            condition="equals"
        )
    ]
    created = criterion_repo.create_with_conditions(sample_criterion, conditions)

    # Delete it
    assert criterion_repo.delete(created.id) is True
    assert criterion_repo.find_by_id(created.id) is None
    # Verify conditions were also deleted
    assert len(criterion_repo.condition_repo.find_by_criterion(created.id)) == 0