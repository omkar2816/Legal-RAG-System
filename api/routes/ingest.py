"""
Document ingestion API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import requests
import os
import re
import time
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
from vectordb.pinecone_client import upsert_embeddings, delete_by_doc_id
from vectordb.advanced_retrieval import retrieve_documents_advanced
from llm_service.llm_client import llm_client
from utils.file_utils import file_utils
from utils.validation import validation_utils
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Document Ingestion"])

# Router for HackRx endpoints without the /ingest prefix
hackrx_router = APIRouter(tags=["HackRx"])

@hackrx_router.post("/run")
async def run_api(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    questions: str = Form(...),
    current_user: Dict[str, Any] = Depends(get_current_user) if settings.ENABLE_AUTH else None
):
    """
    HackRx Run API - Combined document upload and question answering
    
    This endpoint allows users to upload multiple documents and ask multiple questions about them in one step.
    It combines the functionality of /ingest/upload and /query/ask endpoints.
    
    Args:
        files: List of document files to upload and process
        questions: Comma-separated list of questions to ask about the documents
        
    Returns:
        Document processing status and answers to questions
    """
    try:
        # Start timing the request for performance monitoring
        start_time = datetime.now()
        
        # Convert comma-separated questions string to list
        questions_list = [q.strip() for q in questions.split(',')] if questions else []
        
        if not questions_list:
            raise HTTPException(status_code=400, detail="At least one question is required")
            
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="At least one file must be uploaded")
            
        # Log the request details for debugging
        logger.info(f"Processing request with {len(files)} files and {len(questions_list)} questions")
        logger.info(f"File types: {[f.content_type for f in files]}")
        logger.info(f"File sizes: {[f.size for f in files]}")
        
        # Check for very large files early and warn
        for file in files:
            if file.size > 5 * 1024 * 1024:  # 5MB
                logger.warning(f"Large file detected: {file.filename} ({file.size/1024/1024:.2f} MB). Processing may take longer.")
        
        # Process all uploaded files
        processed_documents = []
        doc_titles = []
        
        # Set a timeout for document processing to prevent long-running operations
        doc_processing_timeout = 120  # seconds
        
        for file in files:
            # Validate file upload
            validation_result = validation_utils.validate_file_upload(
                filename=file.filename,
                file_size=file.size,
                content_type=file.content_type
            )
            
            if not validation_result["valid"]:
                processed_documents.append({
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "file_size": file.size,
                    "processing_status": "failed",
                    "errors": validation_result["errors"],
                    "warnings": validation_result.get("warnings", [])
                })
                continue
            
            # Skip unsupported file types early
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in [".pdf", ".txt", ".docx", ".doc", ".png", ".jpg", ".jpeg"]:
                processed_documents.append({
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "file_size": file.size,
                    "processing_status": "failed",
                    "error": f"Unsupported file type: {file_ext}"
                })
                continue
            
            try:
                # Save uploaded file
                file_content = await file.read()
                saved_file_path = file_utils.save_uploaded_file(file_content, file.filename)
                file_size_mb = os.path.getsize(saved_file_path) / (1024 * 1024)
                
                logger.info(f"Processing file: {file.filename} ({file_size_mb:.2f} MB)")
                
                # Process document in background
                doc_type = "policy"  # Default document type
                doc_title = file.filename
                doc_titles.append(doc_title)  # Add to list of processed document titles
                
                # Process document synchronously with timeout protection
                try:
                    start_process_time = datetime.now()
                    await process_document_sync(
                        saved_file_path,
                        file.filename,
                        file.content_type,
                        doc_type,
                        doc_title,
                        None  # No author information
                    )
                    process_time = (datetime.now() - start_process_time).total_seconds()
                    logger.info(f"Document processing completed in {process_time:.2f} seconds")
                    
                    processed_documents.append({
                        "filename": file.filename,
                        "content_type": file.content_type,
                        "file_size": file.size,
                        "processing_status": "completed",
                        "processing_time": f"{process_time:.2f} seconds",
                        "warnings": validation_result.get("warnings", [])
                    })
                except Exception as e:
                    logger.error(f"Error processing document {file.filename}: {e}")
                    processed_documents.append({
                        "filename": file.filename,
                        "content_type": file.content_type,
                        "file_size": file.size,
                        "processing_status": "failed",
                        "error": f"Processing timeout or error: {str(e)}"
                    })
                
            except Exception as e:
                logger.error(f"Error saving file {file.filename}: {e}")
                processed_documents.append({
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "file_size": file.size if hasattr(file, 'size') else 0,
                    "processing_status": "failed",
                    "error": f"Error saving file: {str(e)}"
                })
        
        # Check if any documents were successfully processed
        if not doc_titles:
            raise HTTPException(status_code=400, detail="No documents were successfully processed")
        
        # Process each question and collect answers with performance optimizations
        answers = []
        query_start_time = datetime.now()
        
        # Skip question processing if no documents were successfully processed
        if not any(doc.get("processing_status") == "completed" for doc in processed_documents):
            logger.warning("Skipping question processing as no documents were successfully processed")
            for question in questions_list:
                answers.append({
                    "question": question,
                    "answer": "No documents were successfully processed. Please try uploading documents again.",
                    "status": "error"
                })
        else:
            for question in questions_list:
                try:
                    question_start_time = datetime.now()
                    logger.info(f"Processing question: {question}")
                    
                    # Validate query
                    validation_result = validation_utils.validate_query(question)
                    if not validation_result["valid"]:
                        answers.append({
                            "question": question,
                            "answer": f"Error: {validation_result['errors']}",
                            "status": "error",
                            "processing_time": "0.00 seconds"
                        })
                        continue
                    
                    # Use advanced retrieval with document filter for all processed documents
                    # We don't filter by doc_title to allow cross-document queries
                    try:
                        advanced_results = retrieve_documents_advanced(
                            query=validation_result["cleaned_query"],
                            top_k=1,  # Default value for /hackrx/run endpoint
                            threshold=None,  # Set similarity threshold to null
                            return_count=1,  # Default value for /hackrx/run endpoint
                            adaptive_threshold=settings.ADAPTIVE_THRESHOLD
                        )
                        
                        # Convert advanced results to the format expected by LLM client
                        filtered_results = []
                        for result in advanced_results:
                            match = {
                                'score': result['similarity_score'],
                                'metadata': {
                                    'doc_id': result['doc_id'],
                                    'doc_title': result['doc_title'],
                                    'section_title': result['section_title'],
                                    'text': result['text'],
                                    'page_number': result['page_number'],
                                    'chunk_id': result['chunk_id'],
                                    'word_count': result['word_count'],
                                    'legal_density': result['legal_density']
                                }
                            }
                            filtered_results.append(match)
                        
                        if not filtered_results:
                            question_time = (datetime.now() - question_start_time).total_seconds()
                            answers.append({
                                "question": question,
                                "answer": "No relevant information found in the uploaded documents.",
                                "status": "no_results",
                                "processing_time": f"{question_time:.2f} seconds"
                            })
                            continue
                        
                        # Generate answer using LLM
                        llm_response = llm_client.generate_legal_response(
                            question=validation_result["cleaned_query"],
                            context_chunks=filtered_results
                        )
                        
                        question_time = (datetime.now() - question_start_time).total_seconds()
                        logger.info(f"Question processed in {question_time:.2f} seconds: {question}")
                        
                        # Handle both old string responses and new structured responses
                        if isinstance(llm_response, dict):
                            # New structured response
                            answer = llm_response.get("answer", "")
                            sources = llm_response.get("sources", [])
                            confidence = llm_response.get("confidence", 0.0)
                        else:
                            # Legacy string response
                            answer = llm_response
                            sources = []
                            confidence = 0.0
                        
                        answers.append({
                            "question": question,
                            "answer": answer,
                            "sources": sources,
                            "confidence": confidence,
                            "status": "success",
                            "processing_time": f"{question_time:.2f} seconds"
                        })
                    except Exception as e:
                        logger.error(f"Error retrieving documents for question '{question}': {str(e)}")
                        answers.append({
                            "question": question,
                            "answer": f"Error retrieving documents: {str(e)}",
                            "status": "error",
                            "processing_time": f"{(datetime.now() - question_start_time).total_seconds():.2f} seconds"
                        })
                except Exception as e:
                    logger.error(f"Error processing question '{question}': {e}")
                    answers.append({
                        "question": question,
                        "answer": f"Error: {str(e)}",
                        "status": "error",
                        "processing_time": f"{(datetime.now() - question_start_time).total_seconds() if 'question_start_time' in locals() else 0.0:.2f} seconds"
                    })
        
        # Calculate total processing time
        total_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Total request processing time: {total_time:.2f} seconds")
        
        # Return success status and answers with timing information
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": f"{len(processed_documents)} documents processed and {len(questions_list)} questions answered",
                "documents": processed_documents,
                "questions": questions_list,
                "answers": answers,
                "processing_time": f"{total_time:.2f} seconds"
            }
        )
        
    except Exception as e:
        # Calculate time even for errors
        if 'start_time' in locals():
            error_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error in HackRx Run API after {error_time:.2f} seconds: {e}")
        else:
            logger.error(f"Error in HackRx Run API: {e}")
            
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

async def process_document_sync(
    file_path: str,
    filename: str,
    content_type: str,
    doc_type: str = "unknown",
    doc_title: str = None,
    doc_author: str = None
):
    """
    Process a document synchronously: extract text, chunk, generate embeddings, and store
    This function is similar to process_document but runs synchronously for immediate processing
    Optimized for better performance with caching and efficient processing
    """
    start_time = datetime.now()
    try:
        logger.info(f"Processing document synchronously: {filename}")
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        logger.info(f"File size: {file_size:.2f} MB")
        
        # Skip very large files with a warning
        if file_size > 20:  # 20MB
            logger.warning(f"File too large to process efficiently: {filename} ({file_size:.2f} MB)")
            raise ValueError(f"File too large to process efficiently: {file_size:.2f} MB. Please split the document into smaller parts.")
        
        # Extract text based on file type with performance optimizations
        extraction_start = datetime.now()
        
        if content_type and content_type == "application/pdf":
            # For PDFs, extract text more efficiently
            text = extract_text_from_pdf(file_path)
            logger.info(f"PDF extraction completed in {(datetime.now() - extraction_start).total_seconds():.2f} seconds")
            
        elif content_type and content_type.startswith("image/"):
            # For images, use OCR with a warning about performance
            logger.warning(f"Processing image with OCR which may take longer: {filename}")
            
            # Skip very large images
            if file_size > 5:  # 5MB
                logger.warning(f"Image too large for efficient OCR: {filename} ({file_size:.2f} MB)")
                raise ValueError(f"Image too large for efficient OCR: {file_size:.2f} MB. Please resize or compress the image.")
                
            text = process_image_with_ocr(file_path)
            logger.info(f"OCR processing completed in {(datetime.now() - extraction_start).total_seconds():.2f} seconds")
            
        else:
            # Assume text file (default for .txt files)
            # Use errors='ignore' to handle encoding issues
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            logger.info(f"Text file reading completed in {(datetime.now() - extraction_start).total_seconds():.2f} seconds")
        
        # Skip empty or very small text
        if not text or len(text) < 10:
            logger.warning(f"Document contains insufficient text: {filename}")
            raise ValueError("Document contains insufficient text to process")
        
        # Clean text - only perform essential cleaning
        cleaning_start = datetime.now()
        cleaned_text = clean_text(text)
        logger.info(f"Text cleaning completed in {(datetime.now() - cleaning_start).total_seconds():.2f} seconds")
        
        # Build document metadata
        metadata_start = datetime.now()
        doc_metadata = metadata_builder.build_document_metadata(
            file_path=file_path,
            file_type=content_type,
            content=cleaned_text
        )
        
        # Add additional metadata
        doc_metadata.update({
            "doc_type": doc_type,
            "title": doc_title or filename,
            "author": doc_author or "Unknown",
            "file_size_mb": file_size,
            "processing_time": "pending"
        })
        logger.info(f"Metadata building completed in {(datetime.now() - metadata_start).total_seconds():.2f} seconds")
        
        # Optimize chunking for performance - use a faster chunking method
        chunking_start = datetime.now()
        chunks = []
        
        # Use a more efficient chunking approach based on document size
        if file_size < 1:  # Small files under 1MB
            # For small files, use larger chunks with less overlap
            max_chunk_size = min(settings.MAX_CHUNK_SIZE * 2, 8000)  # Double size but cap at 8000
            
            # Simple chunking by paragraphs
            paragraphs = cleaned_text.split('\n\n')
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) < max_chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append({"text": current_chunk.strip()})
                    current_chunk = para + "\n\n"
            
            # Add the last chunk if it exists
            if current_chunk:
                chunks.append({"text": current_chunk.strip()})
                
        else:  # Larger files
            # For larger files, use smaller chunks to balance performance and quality
            max_chunk_size = settings.MAX_CHUNK_SIZE
            
            # Split by paragraphs first
            paragraphs = cleaned_text.split('\n\n')
            
            # Process paragraphs into chunks
            current_chunk = ""
            for para in paragraphs:
                # If paragraph itself is too large, split it further
                if len(para) > max_chunk_size:
                    # If we have accumulated text, add it as a chunk
                    if current_chunk:
                        chunks.append({"text": current_chunk.strip()})
                        current_chunk = ""
                    
                    # Split large paragraph by sentences
                    sentences = para.split('. ')
                    sentence_chunk = ""
                    
                    for sentence in sentences:
                        if len(sentence_chunk) + len(sentence) < max_chunk_size:
                            sentence_chunk += sentence + ". "
                        else:
                            if sentence_chunk:
                                chunks.append({"text": sentence_chunk.strip()})
                            sentence_chunk = sentence + ". "
                    
                    # Add the last sentence chunk if it exists
                    if sentence_chunk:
                        chunks.append({"text": sentence_chunk.strip()})
                else:
                    # Normal paragraph processing
                    if len(current_chunk) + len(para) < max_chunk_size:
                        current_chunk += para + "\n\n"
                    else:
                        if current_chunk:
                            chunks.append({"text": current_chunk.strip()})
                        current_chunk = para + "\n\n"
            
            # Add the last chunk if it exists
            if current_chunk:
                chunks.append({"text": current_chunk.strip()})
        
        # If no chunks were created, create one with the entire text
        if not chunks and cleaned_text:
            chunks.append({"text": cleaned_text})
            
        logger.info(f"Chunking completed in {(datetime.now() - chunking_start).total_seconds():.2f} seconds. Created {len(chunks)} chunks.")
        
        # Build chunk metadata
        chunk_metadata_list = metadata_builder.build_metadata(
            chunks=chunks,
            doc_id=doc_metadata["doc_id"],
            doc_metadata=doc_metadata
        )
        
        # Generate embeddings with increased batch size for performance
        embedding_start = datetime.now()
        chunk_texts = [chunk["text"] for chunk in chunks]
        
        # Use a larger batch size for better performance, but limit based on number of chunks
        batch_size = min(20, max(5, len(chunk_texts) // 2)) if len(chunk_texts) > 5 else len(chunk_texts)
        embeddings = embedding_client.get_embeddings(chunk_texts, batch_size=batch_size)
        logger.info(f"Embedding generation completed in {(datetime.now() - embedding_start).total_seconds():.2f} seconds")
        
        # Store in vector database
        db_start = datetime.now()
        upsert_embeddings(embeddings, chunk_metadata_list)
        logger.info(f"Database storage completed in {(datetime.now() - db_start).total_seconds():.2f} seconds")
        
        # Move file to processed directory
        file_utils.move_to_processed(file_path, doc_metadata["doc_id"])
        
        total_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Successfully processed document synchronously: {filename} in {total_time:.2f} seconds")
        
        # Update metadata with processing time
        doc_metadata["processing_time"] = f"{total_time:.2f} seconds"
        
        return doc_metadata["doc_id"]
        
    except Exception as e:
        total_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Error processing document synchronously {filename} after {total_time:.2f} seconds: {e}")
        raise ValueError(f"Document processing failed: {str(e)}")