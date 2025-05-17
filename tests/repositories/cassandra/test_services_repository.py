# tests/test_services_repository.py
import pytest
from uuid import UUID
from app.models.schemas import Service, ServiceCreate


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


@pytest.fixture(scope="function")
def bulk_populate_services(service_repo):
    return [service_repo.create(ServiceCreate(
        name=f"test-service-{index}",
        active=True
    )) for index in range(1, 10)]


def test_list_paginated(service_repo, bulk_populate_services):
    active_only = True
    limit = 2
    paging_state = None

    # Loop through pages
    all_results = []
    for _ in range(3):  # Iterate over multiple pages
        # Call the method under test
        result, next_paging_state = service_repo.list_services_paginated(
            active_only=active_only,
            limit=limit,
            paging_state=paging_state,
        )

        # Accumulate results and move to the next page
        all_results.extend(result)
        paging_state = next_paging_state

        if not paging_state:  # Break the loop if there are no more pages
            break

        # Validate that the current page has the correct number of results
        assert len(result) <= limit

    # Ensure all results are filtered by `active_only`
    assert all(service.active for service in all_results)
