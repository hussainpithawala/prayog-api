# app/routers/experiment_routes.py
import base64

import starlette
from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import List, Optional
from app.dependencies import get_experiment_repository
from app.models.schemas import Experiment, ExperimentCreate, ExperimentList
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


@router.get("", response_model=ExperimentList)
async def list_experiments(
        service_id: UUID,
        active_only: bool = False,
        limit: int = Query(10, ge=1, le=100, description="Number of services to return"),
        page_token: Optional[str] = Query(None, description="Token for fetching the next page"),
        repo: ExperimentRepository = Depends(get_experiment_repository)
):
    """
    Paginated list of services. Includes optional filtering by `active_only`.
    """
    # Decode page token from base64 (if provided)
    paging_state = None
    if page_token:
        paging_state = base64.b64decode(page_token)

    # Get paginated results
    services, next_paging_state = repo.list_experiments_paginated_by_service(service_id=service_id,
                                                                             active_only=active_only, limit=limit,
                                                                             paging_state=paging_state
                                                                             )

    # Encode the next page token if it exists
    next_page_token = None
    if next_paging_state:
        next_page_token = base64.b64encode(next_paging_state).decode("utf-8")

    # Return results along with the token for the next page
    return ExperimentList(experiments=services, next_page_token=next_page_token)


@router.delete("/{experiment_id}", status_code=starlette.status.HTTP_202_ACCEPTED)
async def delete_experiment(
        experiment_id: UUID,
        repo: ExperimentRepository = Depends(get_experiment_repository)
):
    result = False
    if not result:
        experiment = repo.find_by_id(experiment_id=experiment_id)
        result = repo.delete(experiment_id=experiment_id)
        if not experiment:
            raise HTTPException(status_code=404, detail="Experiment not found")
        else:
            return {"message": f"experiment {experiment_id} deleted successfully"}
    return None

