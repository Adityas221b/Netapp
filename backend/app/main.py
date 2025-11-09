"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api import data, migration, analytics, ml_api
from app.services.classifier import classifier
from app.ml.access_predictor import predictor

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Classifier initialized with {len(classifier.costs)} tier costs")
    
    if predictor.is_trained:
        logger.info("ML Predictor loaded and ready")
    else:
        logger.warning("ML Predictor not trained - predictions will use fallback")
    
    yield
    
    logger.info("Shutting down CloudFlux AI")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Intelligent Multi-Cloud Data Orchestration Platform",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "classifier_active": True,
        "ml_predictor_trained": predictor.is_trained
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to CloudFlux AI - Intelligent Multi-Cloud Data Orchestration",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
app.include_router(data.router, prefix="/api/data", tags=["Data Management"])
app.include_router(migration.router, prefix="/api/migration", tags=["Migration"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(ml_api.router, prefix="/api/ml", tags=["Machine Learning"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
