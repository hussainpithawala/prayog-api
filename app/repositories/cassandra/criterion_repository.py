# app/repositories/cassandra/criterion_repository.py
from uuid import UUID, uuid4
from datetime import datetime

from cassandra import ConsistencyLevel
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.management import sync_table
from typing import List, Optional

from cassandra.query import SimpleStatement
from fastapi import Depends

# from app.dependencies import get_condition_repo
from app.models.schemas import (
    ExperimentSamplingCriterion,
    ExperimentSamplingCriterionCreate,
    ExperimentSamplingConditionCreate
)
from app.repositories.cassandra.base_repository import BaseRepository, T
from app.repositories.cassandra.dependencies import get_condition_repo
from app.repositories.cassandra.condition_repository import ExperimentSamplingConditionRepository


class ExperimentSamplingCriterionModel(Model):
    __keyspace__ = "experimentation"
    __table_name__ = "experiment_sampling_criteria"

    id = columns.UUID(primary_key=True, default=uuid4)  # primary key
    experiment_id = columns.UUID(primary_key=True)  # partition key
    sampling_model = columns.Text(required=True)  # clustering key
    sampling_attribute = columns.Text(required=True)
    created_at = columns.DateTime(default=datetime.now)
    updated_at = columns.DateTime(default=datetime.now)


class ExperimentSamplingCriterionRepository(BaseRepository):

    def __init__(self, condition_repo: ExperimentSamplingConditionRepository = None):
        super().__init__()
        sync_table(ExperimentSamplingCriterionModel)
        self.condition_repo = condition_repo or get_condition_repo()

    def _sync_table(self):
        sync_table(ExperimentSamplingCriterionModel)

    def update(self, entity: T) -> T:
        pass

    def create(self, criterion: ExperimentSamplingCriterionCreate) -> ExperimentSamplingCriterion:
        criterion_model = ExperimentSamplingCriterionModel.create(
            experiment_id=criterion.experiment_id,
            sampling_model=criterion.sampling_model,
            sampling_attribute=criterion.sampling_attribute
        )
        return ExperimentSamplingCriterion(
            id=criterion_model.id,
            experiment_id=criterion_model.experiment_id,
            sampling_model=criterion_model.sampling_model,
            sampling_attribute=criterion_model.sampling_attribute,
            conditions=[],
            created_at=criterion_model.created_at,
            updated_at=criterion_model.updated_at
        )

    def create_with_conditions(
            self,
            criterion: ExperimentSamplingCriterionCreate,
            conditions: List[ExperimentSamplingConditionCreate]
    ) -> ExperimentSamplingCriterion:
        created_criterion = self.create(criterion)

        # Create associated conditions
        for condition in conditions:
            condition.criterion_id = created_criterion.id
            condition.experiment_id = criterion.experiment_id
            self.condition_repo.create(condition)

        return self.find_by_id(created_criterion.id)

    def find_by_id(self, experiment_sampling_criterion_id: UUID) -> Optional[ExperimentSamplingCriterion]:
        criterion = ExperimentSamplingCriterionModel.objects(
            id=experiment_sampling_criterion_id).allow_filtering().first()
        if not criterion:
            return None

        conditions = self.condition_repo.find_by_criterion(experiment_sampling_criterion_id)
        return ExperimentSamplingCriterion(
            id=criterion.id,
            experiment_id=criterion.experiment_id,
            sampling_model=criterion.sampling_model,
            sampling_attribute=criterion.sampling_attribute,
            conditions=conditions,
            created_at=criterion.created_at,
            updated_at=criterion.updated_at
        )

    def find_by_experiment(self, experiment_id: UUID) -> List[ExperimentSamplingCriterion]:
        criteria = ExperimentSamplingCriterionModel.objects(experiment_id=experiment_id).allow_filtering()
        return [self.find_by_id(c.id) for c in criteria]

    def list_criterions_paginated_by_experiment(self, experiment_id: UUID, limit: int = 100,
                                                paging_state: bytes = None):
        query = f"SELECT * FROM {ExperimentSamplingCriterionModel.__table_name__} WHERE experiment_id = {experiment_id} ALLOW FILTERING"

        statement = SimpleStatement(query, fetch_size=limit, consistency_level=ConsistencyLevel.QUORUM)

        # Execute query with paging state
        result_set = self.session.execute(statement, paging_state=paging_state)
        rows = result_set.current_rows

        # Convert rows to ExperimentSamplingCriterion objects
        criterions = [ExperimentSamplingCriterion(**row) for row in rows]
        return criterions, result_set.paging_state

    def delete(self, experiment_sampling_criterion_id: UUID) -> bool:
        # First delete all associated conditions
        conditions = self.condition_repo.find_by_criterion(experiment_sampling_criterion_id)
        for condition in conditions:
            self.condition_repo.delete(condition.id)

        # Then delete the criterion
        deleted = ExperimentSamplingCriterionModel.objects(id=experiment_sampling_criterion_id).delete()
        return deleted is None

