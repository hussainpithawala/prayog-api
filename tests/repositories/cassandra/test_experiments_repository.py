# tests/test_experiments_repository.py
import pytest
from uuid import UUID
from datetime import datetime
from app.models.schemas import Experiment


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