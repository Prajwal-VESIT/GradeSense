"""
GradeSense FastAPI Backend Application.
Entry point for the REST API providing dataset exploration, analytics,
model comparison, and predictive inference.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import API_TITLE, API_DESCRIPTION, API_VERSION, CORS_ORIGINS
from app.routes.health import router as health_router
from app.routes.data import router as data_router
from app.routes.analytics import router as analytics_router
from app.routes.models import router as models_router
from app.routes.predictions import router as predictions_router

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for local Vite frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers under /api prefix
app.include_router(health_router, prefix="/api")
app.include_router(data_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(models_router, prefix="/api")
app.include_router(predictions_router, prefix="/api")


@app.get("/", tags=["Root"])
def root_status():
    """Root health and welcome message."""
    return JSONResponse(
        content={
            "name": "GradeSense API",
            "status": "online",
            "version": API_VERSION,
            "docs": "/docs",
        }
    )
