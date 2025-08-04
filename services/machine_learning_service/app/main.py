from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import movies, series  # ✅ app.api.routes değil!
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Machine Learning API başlatılıyor...")
    yield
    # Shutdown
    logger.info("🛑 Machine Learning API kapanıyor...")

app = FastAPI(
    title="Machine Learning API",
    description="AWS Personalize ile film ve dizi önerileri",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(movies.router, prefix="/api/movies", tags=["movies"])
app.include_router(series.router, prefix="/api/series", tags=["series"])

@app.get("/")
async def root():
    return {
        "message": "Machine Learning API çalışıyor! 🚀",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "machine-learning-api",
        "version": "1.0.0"
    }