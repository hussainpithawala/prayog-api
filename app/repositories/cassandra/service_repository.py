# app/repositories/service_repository.py
import datetime
import uuid
from typing import List, Optional
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from app.models.schemas import Service, ServiceCreate
from app.repositories.cassandra.base_repository import BaseRepository
from uuid import UUID
from cassandra.cqlengine.query import DoesNotExist
from cassandra.cqlengine.management import sync_table


class ServiceModel(Model):
    __keyspace__ = "experimentation"
    __table_name__ = "services"

    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    name = columns.Text(required=True, index=True)
    active = columns.Boolean(default=True)
    created_at = columns.DateTime()
    updated_at = columns.DateTime()


class ServiceRepository(BaseRepository):
    def _sync_table(self):
        sync_table(ServiceModel)

    def create(self, service: ServiceCreate) -> Service:
        service_model = ServiceModel.create(
            id=uuid.uuid4(),
            name=service.name,
            active=service.active,
            created_at=service.created_at if hasattr(service, 'created_at') else datetime.datetime.now(),
            updated_at=service.updated_at if hasattr(service, 'updated_at') else datetime.datetime.now()
        )
        return Service(**service_model)

    def find_by_id(self, id: UUID) -> Optional[Service]:
        service = ServiceModel.objects(id=id).first()
        return Service(**service) if service else None

    def find_by_name(self, name: str) -> Optional[Service]:
        service = ServiceModel.objects(name=name).first()
        return Service(**service) if service else None

    def list_all(self, active_only: bool = True) -> List[Service]:
        services = ServiceModel.objects.all()
        if active_only:
            return [Service(**s) for s in services if s.active]
        else:
            return [Service(**s) for s in services]


    def update(self, service: Service) -> Service:
        service_model = ServiceModel.objects(id=service.id).first()
        if not service_model:
            raise ValueError("Service not found")

        service_model.update(
            name=service.name,
            active=service.active,
            updated_at=service.updated_at
        )
        return Service(**service_model)

    def delete(self, id: UUID) -> bool:
        """Delete a service by ID. Returns True if deleted, False if not found."""
        try:
            # First verify the service exists
            service = ServiceModel.objects(id=id).first()
            if not service:
                return False

            # Delete the service
            ServiceModel.objects(id=id).delete()
            return True
        except DoesNotExist:
            return False
        except Exception:
            # Log the error if needed
            return False