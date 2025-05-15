# app/routers/experiments.py
from fastapi import APIRouter, Depends, HTTPException
from app.db.cassandra_repository import CassandraRepository
from app.models.schemas import (
    Experiment, ExperimentCreate, ExperimentBucketCreate,
    BucketedSampleCreate
)

router = APIRouter()
repo = CassandraRepository()

@router.post("/", response_model=Experiment)
async def create_experiment(experiment: ExperimentCreate):
    return repo.create_experiment(experiment)

@router.post("/{experiment_id}/buckets", response_model=ExperimentBucket)
async def add_bucket(experiment_id: UUID, bucket: ExperimentBucketCreate):
    return repo.add_bucket(experiment_id, bucket)

@router.post("/{experiment_id}/samples", response_model=BucketedSample)
async def add_sample(experiment_id: UUID, sample: BucketedSampleCreate):
    return repo.add_sample(experiment_id, sample)

# Other endpoints...