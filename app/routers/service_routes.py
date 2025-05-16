# app/routers/service_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List
from app.dependencies import get_service_repository
from app.models.schemas import Service, ServiceCreate
from app.repositories.cassandra.service_repository import ServiceRepository

router = APIRouter(prefix="/api/v1/services", tags=["services"])

@router.post("", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate,
    repo: ServiceRepository = Depends(get_service_repository)
):
    return repo.create(service)

@router.get("", response_model=List[Service])
async def list_services(
    active_only: bool = False,
    repo: ServiceRepository = Depends(get_service_repository)
):
    return repo.list_all(active_only=active_only)

@router.get("/{service_id}", response_model=Service)
async def get_service(
    service_id: UUID,
    repo: ServiceRepository = Depends(get_service_repository)
):
    service = repo.find_by_id(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service