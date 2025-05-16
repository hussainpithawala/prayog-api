from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.cassandra import init_cassandra, close_cassandra
from app.telemetry.tracing import setup_tracing
from app.telemetry.metrics import setup_metrics
from app.telemetry.logging import setup_logging
from app.routers import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_cassandra()
    setup_metrics()
    setup_logging()
    yield
    # Shutdown logic
    close_cassandra()


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


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
