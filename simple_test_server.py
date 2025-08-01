#!/usr/bin/env python3
"""
Simple test server for upload testing
"""
import os
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Simple Test Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Simple Test Server", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/ingest/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = "unknown",
    doc_title: str = None,
    doc_author: str = None
):
    """
    Test upload endpoint that validates the metadata generation
    """
    try:
        # Read file content
        file_content = await file.read()
        content = file_content.decode('utf-8')
        
        print(f"Uploaded file: {file.filename}")
        print(f"Content length: {len(content)} characters")
        
        # Test metadata generation
        from chunking.metadata_builder import metadata_builder
        from chunking.chunker import legal_chunker
        from ingestion.textCleaner import clean_text
        
        # Clean and chunk the text
        cleaned_text = clean_text(content)
        chunks = legal_chunker.chunk_text(cleaned_text, preserve_sections=True)
        
        print(f"Generated {len(chunks)} chunks")
        
        # Build metadata
        doc_metadata = {
            "doc_type": doc_type,
            "title": doc_title or file.filename,
            "author": doc_author or "Unknown"
        }
        
        chunk_metadata_list = metadata_builder.build_metadata(
            chunks=chunks,
            doc_id="test_doc_123",
            doc_metadata=doc_metadata
        )
        
        print(f"Generated metadata for {len(chunk_metadata_list)} chunks")
        
        # Check metadata format
        all_valid = True
        for i, metadata in enumerate(chunk_metadata_list):
            if 'legal_terms' in metadata:
                if not isinstance(metadata['legal_terms'], list):
                    print(f"❌ Chunk {i}: legal_terms is {type(metadata['legal_terms'])} instead of list")
                    all_valid = False
                else:
                    print(f"✅ Chunk {i}: legal_terms is list with {len(metadata['legal_terms'])} items")
        
        if all_valid:
            return JSONResponse(
                status_code=202,
                content={
                    "message": "Document uploaded successfully and processing started",
                    "file_path": f"uploads/{file.filename}",
                    "warnings": [],
                    "metadata_valid": True
                }
            )
        else:
            return JSONResponse(
                status_code=422,
                content={
                    "detail": "Metadata validation failed - legal_terms format is incorrect"
                }
            )
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting simple test server...")
    print("📝 This server tests the upload functionality")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("🔧 Press Ctrl+C to stop the server")
    
    uvicorn.run(app, host="127.0.0.1", port=8000) 