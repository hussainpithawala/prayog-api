# app/repositories/sample_repository.py
import uuid
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from cassandra import ConsistencyLevel
from cassandra.cluster import Session
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.query import BatchStatement

from app.db.cassandra import CassandraSessionManager
from app.models.schemas import BucketedSample, BucketedSampleCreate
from app.repositories.cassandra.base_repository import BaseRepository, T, K
from cassandra.cqlengine.management import sync_table


class BucketedSampleModel(Model):
    __keyspace__ = "experimentation"
    __table_name__ = "bucketed_samples"
    id = columns.UUID(primary_key=True, default=uuid.uuid4)  # Primary key
    experiment_id = columns.UUID(primary_key=True)  # Partition key
    sampled_entity = columns.Text(primary_key=True)  # Clustering column
    sampled_value = columns.Text(required=True)
    created_at = columns.DateTime(primary_key=True, clustering_order="DESC")
    allocated_bucket = columns.Text(required=True)
    complete = columns.Boolean(default=False)
    completed_at = columns.DateTime()
    updated_at = columns.DateTime()


class BucketedSampleRepository(BaseRepository):

    def __init__(self):
        self.session: Session = CassandraSessionManager.get_session()
        super().__init__()

    def find_by_id(self, bucketed_sample_id: UUID) -> Optional[BucketedSample]:
        sample = BucketedSampleModel.objects(id=bucketed_sample_id).first()
        return BucketedSample(**sample)

    def update(self, entity: T) -> T:
        pass

    def _sync_table(self):
        sync_table(BucketedSampleModel)

    def create(self, sample: BucketedSampleCreate) -> BucketedSample:
        sample_model = BucketedSampleModel.create(
            experiment_id=sample.experiment_id,
            sampled_entity=sample.sampled_entity,
            sampled_value=sample.sampled_value,
            allocated_bucket=sample.allocated_bucket,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return BucketedSample(**sample_model)

    def mark_complete(self, experiment_id: UUID, sampled_entity: str, sampled_value: str) -> BucketedSample:
        sample = BucketedSampleModel.objects(
            experiment_id=experiment_id,
            sampled_entity=sampled_entity,
            sampled_value=sampled_value
        ).allow_filtering().first()

        if not sample:
            raise ValueError("Sample not found")

        sample.update(
            complete=True,
            completed_at=datetime.now(),
            updated_at=datetime.now()
        )
        return BucketedSample(**sample)

    def find_by_entity_value(self, experiment_id: UUID, sampled_entity: str, sampled_value: str) -> Optional[
        BucketedSample]:
        sample = BucketedSampleModel.objects(
            experiment_id=experiment_id,
            sampled_entity=sampled_entity,
            sampled_value=sampled_value
        ).allow_filtering().first()
        return BucketedSample(**sample) if sample else None

    def list_by_experiment(self, experiment_id: UUID, limit: int = 100) -> List[BucketedSample]:
        samples = BucketedSampleModel.objects(
            experiment_id=experiment_id
        ).allow_filtering().limit(limit)
        return [BucketedSample(**s) for s in samples]

    def delete(self, experiment_id: UUID) -> bool:
        pass

    def delete_by_experiment(self, experiment_id: UUID) -> bool:
        delete_stmt = self.session.prepare(
            "DELETE FROM bucketed_samples WHERE experiment_id = ?"
        )
        delete_stmt.bind(experiment_id)
        try:
            self.session.execute(delete_stmt)
            return True
        except Exception as e:
            # Log the error
            return False
