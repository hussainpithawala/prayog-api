# app/routers/criterion_routes.py
from fastapi import APIRouter, Depends
from uuid import UUID
from typing import List
from app.dependencies import get_criterion_repository
from app.models.schemas import (
    ExperimentSamplingCriterion,
    ExperimentSamplingCriterionCreate,
    ExperimentSamplingCondition, ExperimentSamplingConditionCreate
)
from app.repositories.cassandra.criterion_repository import ExperimentSamplingCriterionRepository

router = APIRouter(prefix="/api/v1/experiments/{experiment_id}/criteria", tags=["sampling criteria"])

@router.post("", response_model=ExperimentSamplingCriterion)
async def create_criterion(
    experiment_id: UUID,
    criterion: ExperimentSamplingCriterionCreate,
    conditions: List[ExperimentSamplingConditionCreate],
    repo: ExperimentSamplingCriterionRepository = Depends(get_criterion_repository)
):
    criterion.experiment_id = experiment_id
    return repo.create_with_conditions(criterion, conditions)

@router.get("", response_model=List[ExperimentSamplingCriterion])
async def list_criteria(
    experiment_id: UUID,
    repo: ExperimentSamplingCriterionRepository = Depends(get_criterion_repository)
):
    return repo.find_by_experiment(experiment_id)