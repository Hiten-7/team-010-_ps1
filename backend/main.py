from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.config import settings
from backend.database import engine, Base
from backend.routers import disasters, districts, alerts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Disaster Management System...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    # Shutdown
    logger.info("Shutting down Disaster Management System...")


app = FastAPI(
    title="Disaster Management Intelligence System",
    description="AI-driven predictive intelligence for Indian district disaster management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(disasters.router, prefix="/api/v1/disasters", tags=["Disasters"])
app.include_router(districts.router, prefix="/api/v1/districts", tags=["Districts"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Disaster Management Intelligence System API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }
