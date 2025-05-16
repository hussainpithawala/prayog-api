# app/routers/bucket_routes.py
from fastapi import APIRouter, Depends
from uuid import UUID
from typing import List
from app.dependencies import get_bucket_repository
from app.models.schemas import ExperimentBucket, ExperimentBucketCreate
from app.repositories.cassandra.bucket_repository import BucketRepository

router = APIRouter(prefix="/api/v1/experiments/{experiment_id}/buckets", tags=["buckets"])

@router.post("", response_model=ExperimentBucket)
async def create_bucket(
    experiment_id: UUID,
    bucket: ExperimentBucketCreate,
    repo: BucketRepository = Depends(get_bucket_repository)
):
    bucket.experiment_id = experiment_id
    return repo.create(bucket)

@router.get("", response_model=List[ExperimentBucket])
async def list_buckets(
    experiment_id: UUID,
    repo: BucketRepository = Depends(get_bucket_repository)
):
    return repo.list_by_experiment(experiment_id)