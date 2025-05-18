# app/repositories/experiment_repository.py
from uuid import uuid4, UUID
from typing import List, Optional

from cassandra import ConsistencyLevel
from cassandra.cqlengine import columns
from cassandra.cqlengine.connection import session
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import DoesNotExist
from cassandra.query import SimpleStatement

from app.models.schemas import Experiment, ExperimentCreate
from app.repositories.cassandra.base_repository import BaseRepository
from cassandra.cqlengine.management import sync_table
from datetime import datetime


class ExperimentModel(Model):
    __keyspace__ = "experimentation"
    __table_name__ = "experiments"

    id = columns.UUID(primary_key=True)  # Primary key
    service_id = columns.UUID(primary_key=True)  # Partition key
    name = columns.Text(primary_key=True)  # Clustering column
    active = columns.Boolean(default=True)
    last_deactivated_at = columns.DateTime()
    last_activated_at = columns.DateTime()
    scheduled_start_date = columns.DateTime()
    created_at = columns.DateTime()
    updated_at = columns.DateTime()


class ExperimentRepository(BaseRepository):
    def _sync_table(self):
        sync_table(ExperimentModel)

    def create(self, experiment: ExperimentCreate) -> Experiment:
        experiment_model = ExperimentModel.create(
            id=uuid4(),
            service_id=experiment.service_id,
            name=experiment.name,
            active=experiment.active,
            scheduled_start_date=experiment.scheduled_start_date,
            created_at=experiment.created_at if hasattr(experiment, 'created_at') else datetime.now(),
            updated_at=experiment.updated_at if hasattr(experiment, 'updated_at') else datetime.now()
        )
        return Experiment(**experiment_model)

    def find_by_id(self, experiment_id: UUID) -> Optional[Experiment]:
        experiment = ExperimentModel.objects(id=experiment_id).first()
        return Experiment(**experiment) if experiment else None

    def find_by_service_and_name(self, service_id: UUID, name: str) -> Optional[Experiment]:
        experiment = ExperimentModel.objects(service_id=service_id, name=name).allow_filtering().first()
        return Experiment(**experiment) if experiment else None

    def list_by_service(self, service_id: UUID, active_only: bool = True) -> List[Experiment]:
        experiments = ExperimentModel.objects(service_id=service_id).allow_filtering()
        if active_only:
            return [Experiment(**e) for e in experiments if e.active]
        else:
            return [Experiment(**e) for e in experiments]

    def list_experiments_paginated_by_service(self, service_id: UUID, active_only: bool or False, limit: int,
                                              paging_state: bytes = None):
        query = f"SELECT * FROM {ExperimentModel.__table_name__}"

        if active_only:
            query += f" WHERE active = {active_only} and service_id = {service_id} ALLOW FILTERING"

        statement = SimpleStatement(query, fetch_size=limit, consistency_level=ConsistencyLevel.QUORUM
                                    )

        # Execute query with paging state
        result_set = self.session.execute(statement, paging_state=paging_state)
        rows = result_set.current_rows

        # Convert rows to Service objects
        experiments = [Experiment(**row) for row in rows]
        return experiments, result_set.paging_state

    def update_status(self, experiment_id: UUID, active: bool) -> Experiment:
        experiment = ExperimentModel.objects(id=experiment_id).first()
        if not experiment:
            raise ValueError("Experiment not found")

        update_data = {
            'active': active,
            'updated_at': datetime.now()
        }

        if active:
            update_data['last_activated_at'] = datetime.now()
        else:
            update_data['last_deactivated_at'] = datetime.now()

        experiment.update(**update_data)
        return Experiment(**experiment)

    def update(self, experiment: Experiment) -> Experiment:
        experiment = ExperimentModel.objects(id=experiment.id).first()
        if not experiment:
            raise ValueError("Experiment not found")
        experiment.update(name=experiment.name, active=experiment.active, updated_at=experiment.updated_at)
        return Experiment(**experiment)

    def delete(self, experiment_id: UUID) -> bool:
        try:
            ExperimentModel.objects(id=experiment_id).delete()
            result = True
        except DoesNotExist:
            result = False
        except Exception:
            raise
        return result
