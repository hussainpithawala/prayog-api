# app/routers/experiment_routes.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List
from app.dependencies import get_experiment_repository
from app.models.schemas import Experiment, ExperimentCreate
from app.repositories.cassandra.experiment_repository import ExperimentRepository

router = APIRouter(prefix="/api/v1/services/{service_id}/experiments", tags=["experiments"])

@router.post("", response_model=Experiment)
async def create_experiment(
    service_id: UUID,
    experiment: ExperimentCreate,
    repo: ExperimentRepository = Depends(get_experiment_repository)
):
    experiment.service_id = service_id
    return repo.create(experiment)

@router.get("", response_model=List[Experiment])
async def list_experiments(
    service_id: UUID,
    active_only: bool = False,
    repo: ExperimentRepository = Depends(get_experiment_repository)
):
    return repo.list_by_service(service_id, active_only=active_only)