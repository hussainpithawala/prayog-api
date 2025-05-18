# tests/test_experiment_repository.py
import pytest
from app.models.schemas import Experiment, ServiceCreate, ExperimentCreate


def test_create_experiment(experiment_repo, sample_experiment):
    created_experiment = experiment_repo.create(sample_experiment)
    assert isinstance(created_experiment, Experiment)
    assert created_experiment.name == sample_experiment.name
    assert created_experiment.service_id == sample_experiment.service_id


def test_find_experiment_by_id(experiment_repo, sample_experiment):
    created_experiment = experiment_repo.create(sample_experiment)
    found_experiment = experiment_repo.find_by_id(created_experiment.id)

    assert found_experiment is not None
    assert found_experiment.id == created_experiment.id


def test_list_experiments_by_service(experiment_repo, sample_experiment):
    service_id = sample_experiment.service_id
    initial_count = len(experiment_repo.list_by_service(service_id))
    experiment_repo.create(sample_experiment)
    experiments = experiment_repo.list_by_service(service_id)

    assert len(experiments) == initial_count + 1
    assert experiments[-1].service_id == service_id


@pytest.fixture(scope="function")
def bulk_populate_experiments(service_repo, experiment_repo):
    service = service_repo.create(ServiceCreate(
        name=f"test-service-exp-bulk",
        active=True
    ))
    bulk_experiments = [experiment_repo.create(ExperimentCreate(
        service_id=service.id,
        name=f"test-experiment-{index}",
        active=True
    )) for index in range(1, 10)]

    yield service, bulk_experiments
    for experiment in bulk_experiments:
        experiment_repo.delete(experiment.id)
    service_repo.delete(service.id)


def test_list_paginated_experiments(experiment_repo, bulk_populate_experiments):
    """
    Test paginated listing of experiments from the repository.

    - Verifies pagination works correctly with the repository method.
    - Confirms the `next_page_token` is managed properly.
    """
    service, bulk_experiments = bulk_populate_experiments
    limit = 4  # Number of experiments per page

    # Initialize variables for pagination
    all_experiments = []
    next_page_token = None

    while True:
        # Fetch paginated experiments
        current_page, next_page_token = experiment_repo.list_experiments_paginated_by_service(service_id=service.id,
                                                                                              active_only=True,
                                                                                              limit=limit,
                                                                                              paging_state=next_page_token
                                                                                              )

        # Validate the returned experiments
        assert len(current_page) <= limit
        all_experiments.extend(current_page)

        # Exit loop if there's no next page
        if not next_page_token:
            break

    # Verify all experiments were returned across pages
    assert len(all_experiments) == len(bulk_experiments)
    assert {exp.name for exp in bulk_experiments} == {
        exp.name for exp in all_experiments
    }


def test_update_experiment_status(experiment_repo, sample_experiment):
    created_experiment = experiment_repo.create(sample_experiment)
    updated_experiment = experiment_repo.update_status(created_experiment.id, False)

    assert updated_experiment.active is False
    assert updated_experiment.last_deactivated_at is not None


def test_find_by_service_and_name(experiment_repo, sample_experiment):
    created_experiment = experiment_repo.create(sample_experiment)
    found_experiment = experiment_repo.find_by_service_and_name(
        created_experiment.service_id,
        created_experiment.name
    )

    assert found_experiment is not None
    assert found_experiment.id == created_experiment.id
