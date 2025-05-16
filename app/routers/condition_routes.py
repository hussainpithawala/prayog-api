# app/routers/condition_routes.py
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List
from app.dependencies import get_condition_repository
from app.models.schemas import ExperimentSamplingCondition, ExperimentSamplingConditionCreate
from app.repositories.cassandra.experiment_sampling_condition_repository import ExperimentSamplingConditionRepository

router = APIRouter(prefix="/api/v1/criteria/{criterion_id}/conditions", tags=["sampling conditions"])

@router.post("", response_model=ExperimentSamplingCondition)
async def create_condition(
    criterion_id: UUID,
    condition: ExperimentSamplingConditionCreate,
    repo: ExperimentSamplingConditionRepository = Depends(get_condition_repository)
):
    condition.criterion_id = criterion_id
    return repo.create(condition)

@router.get("", response_model=List[ExperimentSamplingCondition])
async def list_conditions(
    criterion_id: UUID,
    repo: ExperimentSamplingConditionRepository = Depends(get_condition_repository)
):
    return repo.find_by_criterion(criterion_id)