# tests/repositories/cassandra/test_integration.py
import pytest
from uuid import uuid4

from app.models.schemas import ExperimentSamplingCriterionCreate, ExperimentSamplingConditionCreate


def test_repository_integration(criterion_repo, condition_repo):
    # Create a criterion

    criterion = criterion_repo.create(ExperimentSamplingCriterionCreate(
        id=uuid4(),
        experiment_id=uuid4(),
        sampling_model="User",
        sampling_attribute="attributes"
    ))
    # Add conditions separately
    condition1 = condition_repo.create(ExperimentSamplingConditionCreate(
        criterion_id=criterion.id,
        experiment_id=criterion.experiment_id,
        model="User",
        property="country",
        value="US",
        condition="equals"
    ))

    condition2 = condition_repo.create(ExperimentSamplingConditionCreate(
        criterion_id=criterion.id,
        experiment_id=criterion.experiment_id,
        model="User",
        property="age",
        value="30",
        condition="gte"
    ))

    # Verify they're linked
    found = criterion_repo.find_by_id(criterion.id)
    assert found is not None
    assert len(found.conditions) == 2
    assert {c.id for c in found.conditions} == {condition1.id, condition2.id}