"""
Document ingestion API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import logging
import requests
import os
import re
from datetime import datetime
from pathlib import Path

from api.auth import get_current_user
from config.settings import settings
from api.models import AnswerResponse, DocumentQuestionRequest

from ingestion.pdf_extractor import extract_text_from_pdf
from ingestion.ocrProcessor import process_image_with_ocr
from ingestion.textCleaner import clean_text
from chunking.chunker import legal_chunker
from chunking.metadata_builder import metadata_builder
from embeddings.embed_client import embedding_client
from vectordb.pinecone_client import upsert_embeddings
from utils.file_utils import file_utils
from utils.validation import validation_utils
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Document Ingestion"])

# Router for HackRx endpoints without the /ingest prefix
hackrx_router = APIRouter(tags=["HackRx"])

@hackrx_router.post("/run")
async def run_api(
    request: DocumentQuestionRequest = None,
    background_tasks: BackgroundTasks = None,
    current_user: Dict[str, Any] = Depends(get_current_user) if settings.ENABLE_AUTH else None,
    documents: str = Form(None),
    questions: str = Form(None)
):
    """
    Run API
    
    Args:
        request: Request containing document URL and questions (JSON body)
        documents: Document URL (form field)
        questions: Questions (form field)
        
    Returns:
        Success status and processing details
    """
    try:
        # Handle both JSON and form data inputs
        if request is not None:
            # JSON input
            url = request.documents.strip('` ')
            questions_list = request.questions
        else:
            # Form input
            url = documents.strip('` ') if documents else None
            # Convert comma-separated questions string to list
            questions_list = [q.strip() for q in questions.split(',')] if questions else []
            
        if not url:
            raise HTTPException(status_code=400, detail="Document URL is required")
            
        if not questions_list:
            raise HTTPException(status_code=400, detail="At least one question is required")
            
        questions = questions_list
        
        logger.info(f"Downloading document from URL: {url}")
        # Download file from URL
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Get filename from URL or Content-Disposition header
        filename = None
        if "Content-Disposition" in response.headers:
            content_disposition = response.headers["Content-Disposition"]
            filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if filename_match:
                filename = filename_match.group(1)
        
        if not filename:
            # Extract filename from URL
            filename = os.path.basename(url.split('?')[0])
            
        if not filename or filename == '':
            # Use a default filename if none could be determined
            filename = f"document_from_url_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Get content type
        content_type = response.headers.get('Content-Type', '')
        
        # Validate file
        file_size = int(response.headers.get('Content-Length', 0))
        validation_result = validation_utils.validate_file_upload(
            filename=filename,
            file_size=file_size,
            content_type=content_type
        )
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation_result["errors"], "warnings": validation_result["warnings"]}
            )
        
        # Save downloaded file
        file_content = response.content
        saved_file_path = file_utils.save_uploaded_file(file_content, filename)
        
        # Process document in background
        background_tasks.add_task(
            process_document,
            saved_file_path,
            filename,
            content_type,
            "policy",  # Document type
            None,  # Document title
            None  # No author information
        )
        
        # Return success status and processing details
        return JSONResponse(
            status_code=202,
            content={
                "status": "success",
                "message": "Document downloaded successfully and processing started",
                "file_path": saved_file_path,
                "filename": filename,
                "content_type": content_type,
                "file_size": file_size,
                "questions_received": len(questions),
                "questions": questions,
                "processing_status": "in_progress",
                "warnings": validation_result.get("warnings", [])
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing document from URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = "unknown",
    doc_title: str = None,
    doc_author: str = None,
    current_user: Dict[str, Any] = Depends(get_current_user) if settings.ENABLE_AUTH else None
):
    """
    Upload and process a document for the RAG system
    """
    try:
        # Validate file upload
        validation_result = validation_utils.validate_file_upload(
            filename=file.filename,
            file_size=file.size,
            content_type=file.content_type
        )
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation_result["errors"], "warnings": validation_result["warnings"]}
            )
        
        # Save uploaded file
        file_content = await file.read()
        saved_file_path = file_utils.save_uploaded_file(file_content, file.filename)
        
        # Process document in background
        background_tasks.add_task(
            process_document,
            saved_file_path,
            file.filename,
            file.content_type,
            doc_type,
            doc_title,
            doc_author
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "Document uploaded successfully and processing started",
                "file_path": saved_file_path,
                "warnings": validation_result.get("warnings", [])
            }
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-multiple")
async def upload_multiple_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """
    Upload multiple documents for processing
    """
    results = []
    
    for file in files:
        try:
            # Validate file
            validation_result = validation_utils.validate_file_upload(
                filename=file.filename,
                file_size=file.size,
                content_type=file.content_type
            )
            
            if validation_result["valid"]:
                file_content = await file.read()
                saved_file_path = file_utils.save_uploaded_file(file_content, file.filename)
                
                background_tasks.add_task(
                    process_document,
                    saved_file_path,
                    file.filename,
                    file.content_type
                )
                
                results.append({
                    "filename": file.filename,
                    "status": "accepted",
                    "file_path": saved_file_path
                })
            else:
                results.append({
                    "filename": file.filename,
                    "status": "rejected",
                    "errors": validation_result["errors"]
                })
                
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {"results": results}

@router.get("/status/{doc_id}")
async def get_processing_status(doc_id: str):
    """
    Get the processing status of a document
    """
    # This would typically check a database or cache for processing status
    # For now, return a mock response
    return {
        "doc_id": doc_id,
        "status": "completed",
        "chunks_processed": 10,
        "embeddings_generated": 10,
        "vectors_stored": 10
    }

async def process_document(
    file_path: str,
    filename: str,
    content_type: str,
    doc_type: str = "unknown",
    doc_title: str = None,
    doc_author: str = None
):
    """
    Process a document: extract text, chunk, generate embeddings, and store
    """
    try:
        logger.info(f"Processing document: {filename}")
        
        # Extract text based on file type
        if content_type and content_type == "application/pdf":
            text = extract_text_from_pdf(file_path)
        elif content_type and content_type.startswith("image/"):
            text = process_image_with_ocr(file_path)
        else:
            # Assume text file (default for .txt files)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        # Clean text
        cleaned_text = clean_text(text)
        
        # Build document metadata
        doc_metadata = metadata_builder.build_document_metadata(
            file_path=file_path,
            file_type=content_type,
            content=cleaned_text
        )
        
        # Add additional metadata
        doc_metadata.update({
            "doc_type": doc_type,
            "title": doc_title or filename,
            "author": doc_author or "Unknown"
        })
        
        # Chunk text based on document type
        chunks = legal_chunker.chunk_by_document_type(cleaned_text, doc_type)
        
        # Build chunk metadata
        chunk_metadata_list = metadata_builder.build_metadata(
            chunks=chunks,
            doc_id=doc_metadata["doc_id"],
            doc_metadata=doc_metadata
        )
        
        # Generate embeddings
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_client.get_embeddings(chunk_texts)
        
        # Store in vector database
        upsert_embeddings(embeddings, chunk_metadata_list)
        
        # Move file to processed directory
        processed_path = file_utils.move_to_processed(file_path, doc_metadata["doc_id"])
        
        logger.info(f"Successfully processed document: {filename}")
        
    except Exception as e:
        logger.error(f"Error processing document {filename}: {e}")
        raise