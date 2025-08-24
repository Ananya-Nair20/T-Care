# backend/app/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .config import settings
from .database import engine, Base
from .api.v1 import (
    blood_matching,
    donors,
    patients,
    emergency,
    chat,
)

# -------------------------------------------------
# Logging Configuration
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# FastAPI App Instance
# -------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Thalassemia Care Platform",
)

# -------------------------------------------------
# Middleware
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Database Initialization
# -------------------------------------------------
Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# Routers
# -------------------------------------------------
app.include_router(blood_matching.router, prefix="/api/v1/matching", tags=["Blood Matching"])
app.include_router(donors.router,          prefix="/api/v1/donors",   tags=["Donors"])
app.include_router(patients.router,        prefix="/api/v1/patients", tags=["Patients"])
app.include_router(emergency.router,       prefix="/api/v1/emergency", tags=["Emergency"])
app.include_router(chat.router,            prefix="/api/v1/chat",     tags=["Chat"])
app.include_router(donor_scheduler.router, prefix="/api/v1/scheduler", tags=["Scheduler"])

# -------------------------------------------------
# Routes
# -------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "T-Care Platform API",
        "version": settings.APP_VERSION,
        "status": "operational",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# -------------------------------------------------
# Exception Handlers
# -------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
