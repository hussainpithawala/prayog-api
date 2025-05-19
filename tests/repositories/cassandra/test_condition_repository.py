# tests/repositories/cassandra/test_condition_repository.py
from uuid import uuid4

def test_create_condition(condition_repo, sample_condition):
    created = condition_repo.create(sample_condition)
    assert created.id is not None
    assert created.model == sample_condition.model
    assert created.property == sample_condition.property


def test_find_by_id(condition_repo, sample_condition):
    created = condition_repo.create(sample_condition)
    found = condition_repo.find_by_id(created.id)
    assert found is not None
    assert found.id == created.id


def test_find_by_criterion(condition_repo, sample_condition):
    # Create 2 conditions with same criterion_id
    criterion_id = uuid4()
    sample_condition.criterion_id = criterion_id

    condition1 = condition_repo.create(sample_condition)
    sample_condition.property = "age"
    sample_condition.value = "30"
    condition2 = condition_repo.create(sample_condition)

    conditions = condition_repo.find_by_criterion(criterion_id)
    assert len(conditions) == 2
    assert {c.id for c in conditions} == {condition1.id, condition2.id}


def test_delete_condition(condition_repo, sample_condition):
    created = condition_repo.create(sample_condition)
    assert condition_repo.delete(created.id) is True
    assert condition_repo.find_by_id(created.id) is None