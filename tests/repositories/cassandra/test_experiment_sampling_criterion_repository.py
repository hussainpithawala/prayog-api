# tests/repositories/cassandra/test_experiment_sampling_criterion_repository.py
import pytest
from uuid import uuid4
from app.models.schemas import (
    ExperimentSamplingConditionCreate, ServiceCreate, ExperimentCreate, ExperimentSamplingCriterionCreate
)


def test_create_criterion(criterion_repo, sample_criterion):
    created = criterion_repo.create(sample_criterion)
    assert created.id is not None
    assert created.sampling_model == sample_criterion.sampling_model
    assert len(created.conditions) == 0


def test_create_with_conditions(criterion_repo, sample_criterion):
    conditions = [
        ExperimentSamplingConditionCreate(
            experiment_id=sample_criterion.experiment_id,
            model="User",
            property="country",
            value="US",
            condition="equals"
        ),
        ExperimentSamplingConditionCreate(
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


@pytest.fixture(scope="function")
def bulk_populate_criterion(service_repo, experiment_repo, criterion_repo):
    test_service = service_repo.create(ServiceCreate(
        name=f"test-service-criterion-bulk",
        active=True
    ))
    test_experiment = experiment_repo.create(ExperimentCreate(
        service_id=test_service.id,
        name=f"test-experiment-criterion-bulk",
        active=True
    ))

    test_criterions = [criterion_repo.create(ExperimentSamplingCriterionCreate(
        experiment_id=test_experiment.id,
        sampling_model="test-model",
        sampling_attribute=f"attribute-{index}"
    )) for index in range(1, 10)]

    yield test_service, test_experiment, test_criterions
    experiment_repo.delete(experiment_id=test_experiment.id)
    service_repo.delete(test_service.id)
    for test_criterion in test_criterions:
        criterion_repo.delete(test_criterion.id)


def test_list_paginated_criterions_by_experiment(criterion_repo, bulk_populate_criterion):
    """
    Test paginated listing of sampling criterions from the repository.

    - Verifies pagination works correctly with the repository method.
    - Confirms the `next_page_token` is managed properly.
    """
    test_service, test_experiment, test_criterions = bulk_populate_criterion
    limit = 4  # Number of criterions per page

    # Initialize variables for pagination
    all_criterions = []
    next_page_token = None

    while True:
        # Fetch paginated criterions
        current_page, next_page_token = criterion_repo.list_criterions_paginated_by_experiment(
            experiment_id=test_experiment.id,
            limit=limit,
            paging_state=next_page_token
        )

        # Validate the returned criterions
        assert len(current_page) <= limit
        all_criterions.extend(current_page)

        # Exit loop if there's no next page
        if not next_page_token:
            break

    # Verify all criterions were returned across pages
    assert len(all_criterions) == len(test_criterions)
    assert {criterion.sampling_model for criterion in test_criterions} == {
        criterion.sampling_model for criterion in all_criterions
    }
