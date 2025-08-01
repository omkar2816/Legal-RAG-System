#!/usr/bin/env python3
"""
Test server that bypasses API key requirements to test upload functionality
"""
import os
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routes.ingest import router as ingest_router
from utils.validation import validation_utils
from utils.file_utils import file_utils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Test Legal RAG System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Override the settings to bypass API key requirements
import config.settings
config.settings.settings.VOYAGE_API_KEY = "test_key"
config.settings.settings.PINECONE_API_KEY = "test_key"

# Include ingest router
app.include_router(ingest_router)

@app.get("/")
async def root():
    return {"message": "Test Legal RAG System", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting test server (no API keys required)...")
    print("📝 This server bypasses API key requirements for testing")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("🔧 Press Ctrl+C to stop the server")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True) 