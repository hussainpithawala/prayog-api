# app/routers/service_routes.py
import base64

import starlette.status
from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from typing import List, Optional
from fastapi import Query, Depends
from app.dependencies import get_service_repository
from app.models.schemas import Service, ServiceCreate, ServiceList
from app.repositories.cassandra.service_repository import ServiceRepository

router = APIRouter(prefix="/api/v1/services", tags=["services"])

@router.post("", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate,
    repo: ServiceRepository = Depends(get_service_repository)
):
    return repo.create(service)

@router.get("", response_model=ServiceList)
async def list_services(
        active_only: bool = False,
        limit: int = Query(10, ge=1, le=100, description="Number of services to return"),
        page_token: Optional[str] = Query(None, description="Token for fetching the next page"),
        repo: ServiceRepository = Depends(get_service_repository)
):
    """
    Paginated list of services. Includes optional filtering by `active_only`.
    """
    # Decode page token from base64 (if provided)
    paging_state = None
    if page_token:
        paging_state = base64.b64decode(page_token)

    # Get paginated results
    services, next_paging_state = repo.list_services_paginated(
        active_only=active_only, limit=limit, paging_state=paging_state
    )

    # Encode the next page token if it exists
    next_page_token = None
    if next_paging_state:
        next_page_token = base64.b64encode(next_paging_state).decode("utf-8")

    # Return results along with the token for the next page
    return ServiceList(services=services, next_page_token=next_page_token)


@router.get("/{service_id}", response_model=Service)
async def get_service(
    service_id: UUID,
    repo: ServiceRepository = Depends(get_service_repository)
):
    service = repo.find_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.delete("/{service_id}", status_code=starlette.status.HTTP_202_ACCEPTED)
async def delete_service(
    service_id: UUID,
    repo: ServiceRepository = Depends(get_service_repository)
):
    result = repo.delete(service_id)
    if not result:
        service = repo.find_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        else:
            raise HTTPException(status_code=422, detail="Unable to delete service")
    return {"message": f"service {service_id} deleted successfully"}
