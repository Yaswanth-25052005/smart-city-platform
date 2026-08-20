"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import health, alerts, sensors, analytics, dashboard, devices, locations
from backend.common.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    logger.info("Smart City API starting")
    yield
    logger.info("Smart City API shutting down")


app = FastAPI(
    title="Smart City Analytics Platform API",
    description="REST API for smart city sensor data, analytics, alerts, and predictions.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(sensors.router, prefix="/api/sensors", tags=["sensors"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Smart City Analytics Platform API", "docs": "/docs"}
