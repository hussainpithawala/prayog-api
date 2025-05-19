# app/routers/sample_routes.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List
from app.dependencies import get_sample_repository
from app.models.schemas import BucketedSample, BucketedSampleCreate
from app.repositories.cassandra.sample_repository import BucketedSampleRepository

router = APIRouter(prefix="/api/v1/experiments/{experiment_id}/samples", tags=["samples"])

@router.post("", response_model=BucketedSample)
async def create_sample(
    experiment_id: UUID,
    sample: BucketedSampleCreate,
    repo: BucketedSampleRepository = Depends(get_sample_repository)
):
    sample.experiment_id = experiment_id
    return repo.create(sample)

@router.get("", response_model=List[BucketedSample])
async def list_samples(
    experiment_id: UUID,
    limit: int = 100,
    repo: BucketedSampleRepository = Depends(get_sample_repository)
):
    return repo.list_by_experiment(experiment_id, limit=limit)

@router.post("/{sample_id}/complete", response_model=BucketedSample)
async def mark_sample_complete(
    sample_id: UUID,
    repo: BucketedSampleRepository = Depends(get_sample_repository)
):
    sample = repo.find_by_id(sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return repo.mark_complete(sample.experiment_id, sample.sampled_entity, sample.sampled_value)