from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.db.cassandra import CassandraSessionManager
from app.telemetry.tracing import setup_tracing
from app.telemetry.metrics import setup_metrics
from app.telemetry.logging import setup_logging
from app.routers import router as api_router, docs


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    # Initialize Cassandra connection
    CassandraSessionManager.get_session()
    setup_metrics()
    setup_logging()
    yield
    # Shutdown logic
    # Clean up Cassandra connection
    CassandraSessionManager.shutdown()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Experiment API",
        version="1.0.0",
        description="API for managing experiment samples",
        routes=app.routes,
    )

    # Customize the schema if needed
    # openapi_schema["info"]["x-logo"] = {
    #     "url": "https://your-logo-url.png"
    # }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(
    title="FastAPI Cassandra OpenTelemetry",
    lifespan=lifespan
)

# Setup tracing (needs to be after app creation)
setup_tracing(app)

# Include routers
# app.include_router(items.router, prefix="/items", tags=["items"])
app = FastAPI()
app.include_router(api_router)
app.include_router(docs.router)
app.openapi = custom_openapi


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
