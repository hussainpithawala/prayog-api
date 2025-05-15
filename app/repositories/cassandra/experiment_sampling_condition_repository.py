# app/repositories/cassandra/experiment_sampling_condition_repository.py
from uuid import UUID, uuid4
from datetime import datetime
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.management import sync_table
from typing import List, Optional
from app.models.schemas import ExperimentSamplingCondition, ExperimentSamplingConditionCreate


class ExperimentSamplingConditionModel(Model):
    __keyspace__ = "experimentation"
    __table_name__ = "experiment_sampling_conditions"

    id = columns.UUID(primary_key=True, default=uuid4)
    criterion_id = columns.UUID(primary_key=True)
    experiment_id = columns.UUID(required=True)
    model = columns.Text(required=True)
    property = columns.Text(required=True)
    value = columns.Text(required=True)
    condition = columns.Text(required=True)
    created_at = columns.DateTime(default=datetime.now)
    updated_at = columns.DateTime(default=datetime.now)


class ExperimentSamplingConditionRepository:
    def __init__(self):
        sync_table(ExperimentSamplingConditionModel)

    def create(self, condition: ExperimentSamplingConditionCreate) -> ExperimentSamplingCondition:
        condition_model = ExperimentSamplingConditionModel.create(
            criterion_id=condition.criterion_id,
            experiment_id=condition.experiment_id,
            model=condition.model,
            property=condition.property,
            value=condition.value,
            condition=condition.condition
        )
        return ExperimentSamplingCondition(**condition_model)

    def find_by_id(self, experiment_sampling_condition_id: UUID) -> Optional[ExperimentSamplingCondition]:
        condition = ExperimentSamplingConditionModel.objects(id=experiment_sampling_condition_id).allow_filtering().first()
        return ExperimentSamplingCondition(**condition) if condition else None

    def find_by_criterion(self, criterion_id: UUID) -> List[ExperimentSamplingCondition]:
        conditions = ExperimentSamplingConditionModel.objects(criterion_id=criterion_id).allow_filtering()
        return [ExperimentSamplingCondition(**c) for c in conditions]

    def find_by_experiment(self, experiment_id: UUID) -> List[ExperimentSamplingCondition]:
        conditions = ExperimentSamplingConditionModel.objects(experiment_id=experiment_id)
        return [ExperimentSamplingCondition(**c) for c in conditions]

    def delete(self, id: UUID) -> bool:
        deleted = ExperimentSamplingConditionModel.objects(id=id).delete()
        return deleted is None