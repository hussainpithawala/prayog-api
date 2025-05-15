# tests/test_services_repository.py
import pytest
from uuid import UUID
from app.models.schemas import Service


def test_create_service(service_repo, sample_service):
    created_service = service_repo.create(sample_service)
    assert isinstance(created_service, Service)
    assert created_service.name == sample_service.name
    assert created_service.active is True
    assert isinstance(created_service.id, UUID)


def test_find_service_by_id(service_repo, sample_service):
    created_service = service_repo.create(sample_service)
    found_service = service_repo.find_by_id(created_service.id)

    assert found_service is not None
    assert found_service.id == created_service.id
    assert found_service.name == created_service.name


def test_find_service_by_name(service_repo, sample_service):
    created_service = service_repo.create(sample_service)
    found_service = service_repo.find_by_name(created_service.name)

    assert found_service is not None
    assert found_service.id == created_service.id


def test_update_service(service_repo, sample_service):
    created_service = service_repo.create(sample_service)
    updated_service = service_repo.update(
        Service(
            id=created_service.id,
            name="updated-name",
            active=False,
            created_at=created_service.created_at,
            updated_at=created_service.updated_at
        )
    )

    assert updated_service.name == "updated-name"
    assert updated_service.active is False


def test_delete_service(service_repo, sample_service):
    created_service = service_repo.create(sample_service)
    assert service_repo.delete(created_service.id) is True
    assert service_repo.find_by_id(created_service.id) is None


def test_list_services(service_repo, sample_service):
    initial_count = len(service_repo.list_all())
    service_repo.create(sample_service)
    services = service_repo.list_all()

    assert len(services) == initial_count + 1
    assert services[-1].name == sample_service.name