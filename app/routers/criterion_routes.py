# app/routers/criterion_routes.py
import base64

import starlette
from fastapi import APIRouter, Depends, Query, HTTPException
from uuid import UUID
from typing import List, Optional
from app.dependencies import get_criterion_repository
from app.models.schemas import (
    ExperimentSamplingCriterion,
    ExperimentSamplingCriterionCreate,
    ExperimentSamplingCondition, ExperimentSamplingConditionCreate, ExperimentSamplingCriterionList
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


@router.get("", response_model=ExperimentSamplingCriterionList)
async def list_criterions(
        experiment_id: UUID,
        limit: int = Query(10, ge=1, le=100, description="Number of criterions to return"),
        page_token: Optional[str] = Query(None, description="Token for fetching the next page"),
        repo: ExperimentSamplingCriterionRepository = Depends(get_criterion_repository)
):
    """
    Paginated list of sampling criterions. Includes optional filtering by `active_only`.
    """
    # Decode page token from base64 (if provided)
    paging_state = None
    if page_token:
        paging_state = base64.b64decode(page_token)

    # Get paginated results
    criterions, next_paging_state = repo.list_criterions_paginated_by_experiment(
        experiment_id=experiment_id,
        limit=limit,
        paging_state=paging_state
    )

    # Encode the next page token if it exists
    next_page_token = None
    if next_paging_state:
        next_page_token = base64.b64encode(next_paging_state).decode("utf-8")

    # Return results along with the token for the next page
    return ExperimentSamplingCriterionList(criterions=criterions, next_page_token=next_page_token)


@router.delete("/{criterion_id}", status_code=starlette.status.HTTP_202_ACCEPTED)
async def delete_criterion(
        criterion_id: UUID,
        repo: ExperimentSamplingCriterionRepository = Depends(get_criterion_repository)
):
    result = False
    if not result:
        criterion = repo.find_by_id(experiment_sampling_criterion_id=criterion_id)
        result = repo.delete(experiment_sampling_criterion_id=criterion_id)
        if not criterion:
            raise HTTPException(status_code=404, detail="Criterion not found")
        else:
            return {"message": f"criterion {criterion_id} deleted successfully"}
    return None
