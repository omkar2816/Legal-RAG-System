"""
Main FastAPI application for the Legal RAG System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys

from api.routes import ingest, query, admin
from api.auth import router as auth_router
from vectordb.pinecone_client import create_index
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('legal_rag.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION + """
    
    ## Authentication
    
    This API uses Bearer Token Authentication. To use protected endpoints:
    
    1. Get a token by sending a POST request to `/auth/token` with your username and password
    2. Register a new user by sending a POST request to `/auth/register`
    3. Include the token in the Authorization header of your requests: `Authorization: Bearer {token}`
    
    Some endpoints are public and don't require authentication.
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - Authentication and HackRx endpoints first for better API docs organization
app.include_router(auth_router, prefix="/auth")
app.include_router(ingest.hackrx_router, prefix="/hackrx")
app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup_event():
    """
    Initialize the application on startup
    """
    try:
        logger.info("Starting Legal RAG System...")
        
        # Validate required settings
        if not settings.validate_required_settings():
            logger.error("Missing required environment variables")
            raise Exception("Missing required environment variables")
        
        # Create Pinecone index if it doesn't exist
        create_index()
        
        logger.info("Legal RAG System started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on application shutdown
    """
    logger.info("Shutting down Legal RAG System...")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Legal RAG System API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/admin/health"
    }

@app.get("/health")
async def health():
    """
    Simple health check endpoint
    """
    return {"status": "healthy", "service": "Legal RAG System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
