"""Rediguard Backend - Real-Time Security & Threat Detection MVP"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.redis import redis_client
from app.api.routes import router
from app.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup_event():
    """Main FastAPI application with Redis Stack 8 integration"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.redis_stack import redis_stack_client
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Rediguard backend...")
    
    try:
        # Connect to Redis Stack
        redis_stack_client.connect()
        logger.info("Redis Stack connected successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis Stack: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Rediguard backend...")
    try:
        redis_stack_client.close()
        logger.info("Redis Stack connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis Stack connection: {e}")


# Create FastAPI application
app = FastAPI(
    title="Rediguard Backend",
    description="Real-Time Security & Threat Detection MVP using Redis 8 + AI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Rediguard Backend API",
        "version": "1.0.0",
        "description": "Real-Time Security & Threat Detection MVP using Redis 8 + AI"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis Stack connection
        redis_healthy = redis_stack_client._is_connected
        
        if redis_healthy:
            redis_stack_client.client.ping()
        
        return {
            "status": "healthy" if redis_healthy else "unhealthy",
            "redis_stack": "connected" if redis_healthy else "disconnected",
            "redis_modules": redis_stack_client._modules_available
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "redis_stack": "disconnected"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down Rediguard Backend")
    
    try:
        # Close Redis connection
        redis_client.close()
        logger.info("Shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Rediguard Backend API",
        "version": settings.api_version,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
