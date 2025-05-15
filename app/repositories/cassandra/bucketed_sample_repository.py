# app/repositories/sample_repository.py
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from app.models.schemas import BucketedSample, BucketedSampleCreate
from app.repositories.cassandra.base_repository import BaseRepository
from cassandra.cqlengine.management import sync_table

class BucketedSampleModel(Model):
    __keyspace__ = "experimentation"
    __table_name__ = "bucketed_samples"

    experiment_id = columns.UUID(primary_key=True, partition_key=True)
    sampled_entity = columns.Text(primary_key=True)
    sampled_value = columns.Text(primary_key=True)
    created_at = columns.DateTime(primary_key=True, clustering_order="DESC")
    allocated_bucket = columns.Text(required=True)
    complete = columns.Boolean(default=False)
    completed_at = columns.DateTime()
    updated_at = columns.DateTime()


class BucketedSampleRepository(BaseRepository):
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
        ).first()

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
        ).first()
        return BucketedSample(**sample) if sample else None

    def list_by_experiment(self, experiment_id: UUID, limit: int = 100) -> List[BucketedSample]:
        samples = BucketedSampleModel.objects(
            experiment_id=experiment_id
        ).limit(limit)
        return [BucketedSample(**s) for s in samples]

    def delete(self, experiment_id: UUID) -> bool:
        deleted = BucketedSampleModel.objects(
            experiment_id=experiment_id
        ).delete()
        return deleted > 0