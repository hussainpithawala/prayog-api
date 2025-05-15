# app/repositories/bucket_repository.py
import uuid
from uuid import UUID
from typing import List, Optional
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

from app.models.schemas import ExperimentBucket, ExperimentBucketCreate
from app.repositories.cassandra.base_repository import BaseRepository, T, K
from datetime import datetime
from cassandra.cqlengine.management import sync_table

class ExperimentBucketModel(Model):
    __keyspace__ = "experimentation"
    __table_name__ = "experiment_buckets"
    id = columns.UUID(primary_key=True) # Primary key
    experiment_id = columns.UUID(primary_key=True) # Partition key
    bucket_name = columns.Text(primary_key=True) # Clustering column
    percentage_distribution = columns.Integer(required=True)
    created_at = columns.DateTime()
    updated_at = columns.DateTime()


class BucketRepository(BaseRepository):
    def find_by_id(self, bucket_id: K) -> Optional[T]:
        bucket = ExperimentBucketModel.objects(id = bucket_id).first()
        return ExperimentBucket(**bucket) if bucket else None

    def update(self, entity: T) -> T:
        bucket = ExperimentBucketModel.objects(id = entity.id).first()
        if not bucket:
            raise ValueError(f"No Bucket found for id {entity.id}")
        bucket.update(bucket_name=entity.bucket_name, percentage_distribution=entity.percentage_distribution)
        return ExperimentBucket(**bucket)

    def _sync_table(self):
        sync_table(ExperimentBucketModel)

    def create(self, bucket: ExperimentBucketCreate) -> ExperimentBucket:
        bucket_model = ExperimentBucketModel.create(
            id = uuid.uuid4(),
            experiment_id=bucket.experiment_id,
            bucket_name=bucket.bucket_name,
            percentage_distribution=bucket.percentage_distribution,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return ExperimentBucket(**bucket_model)

    def find_by_experiment_and_name(self, experiment_id: UUID, bucket_name: str) -> Optional[ExperimentBucket]:
        bucket = ExperimentBucketModel.objects(
            experiment_id=experiment_id,
            bucket_name=bucket_name
        ).allow_filtering().first()
        return ExperimentBucket(**bucket) if bucket else None

    def list_by_experiment(self, experiment_id: UUID) -> List[ExperimentBucket]:
        buckets = ExperimentBucketModel.objects(experiment_id=experiment_id).allow_filtering()
        return [ExperimentBucket(**b) for b in buckets]

    def update_distribution(self, experiment_id: UUID, bucket_name: str, percentage: int) -> ExperimentBucket:
        bucket = ExperimentBucketModel.objects(
            experiment_id=experiment_id,
            bucket_name=bucket_name
        ).allow_filtering().first()

        if not bucket:
            raise ValueError("Bucket not found")

        bucket.update(
            percentage_distribution=percentage,
            updated_at=datetime.now()
        )
        return ExperimentBucket(**bucket)

    def delete(self, experiment_id: UUID) -> bool:
        deleted = ExperimentBucketModel.objects(
            experiment_id=experiment_id
        ).delete()
        return deleted > 0