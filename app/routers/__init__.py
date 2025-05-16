from fastapi import APIRouter
from .service_routes import router as service_router
from .experiment_routes import router as experiment_router
from .bucket_routes import router as bucket_router
from .criterion_routes import router as criterion_router
from .condition_routes import router as condition_router
from .sample_routes import router as sample_router

router = APIRouter()
router.include_router(service_router)
