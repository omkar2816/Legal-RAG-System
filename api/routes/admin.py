"""
Admin API endpoints for the Legal RAG System
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

from vectordb.pinecone_client import get_index_stats, delete_by_doc_id
from utils.file_utils import file_utils
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Administration"])

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Check if Pinecone is accessible
        stats = get_index_stats()
        # Convert stats to JSON-serializable format
        if hasattr(stats, 'to_dict'):
            stats = stats.to_dict()
        else:
            try:
                import json
                stats = json.loads(json.dumps(stats))
            except Exception:
                stats = str(stats)
        return {
            "status": "healthy",
            "pinecone_status": "connected",
            "index_stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "pinecone_status": "disconnected",
            "error": str(e)
        }

@router.get("/stats")
async def get_system_stats():
    """
    Get system statistics
    """
    try:
        # Get Pinecone index statistics
        index_stats = get_index_stats()
        # Convert stats to JSON-serializable format
        if hasattr(index_stats, 'to_dict'):
            index_stats = index_stats.to_dict()
        else:
            try:
                import json
                index_stats = json.loads(json.dumps(index_stats))
            except Exception:
                index_stats = str(index_stats)
        
        # Get file statistics
        processed_files = file_utils.list_processed_files()
        
        return {
            "index_stats": index_stats,
            "processed_files": {
                "count": len(processed_files),
                "files": processed_files
            },
            "system_info": {
                "chunk_size": settings.CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
                "embedding_model": settings.EMBEDDING_MODEL,
                "llm_model": settings.GROQ_CHAT_MODEL
            }
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document and all its associated vectors
    """
    try:
        # Delete vectors from Pinecone
        delete_by_doc_id(doc_id)
        
        # Delete processed file
        # Note: This would need to be enhanced to track file paths by doc_id
        # For now, just delete from Pinecone
        
        return {
            "message": f"Document {doc_id} deleted successfully",
            "doc_id": doc_id
        }
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_system():
    """
    Clean up old files and optimize system
    """
    try:
        # Clean up old uploaded files
        file_utils.cleanup_old_files(max_age_days=7)
        
        return {
            "message": "System cleanup completed",
            "cleanup_tasks": ["old_files_removed"]
        }
    except Exception as e:
        logger.error(f"Error during system cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_configuration():
    """
    Get current system configuration (non-sensitive)
    """
    return {
        "chunk_size": settings.CHUNK_SIZE,
        "chunk_overlap": settings.CHUNK_OVERLAP,
        "max_file_size": settings.MAX_FILE_SIZE,
        "allowed_extensions": list(settings.ALLOWED_EXTENSIONS.keys()),
        "top_k_results": settings.TOP_K_RESULTS,
        "similarity_threshold": settings.SEARCH_SIMILARITY_THRESHOLD,
        "embedding_model": settings.EMBEDDING_MODEL,
        "llm_model": settings.GROQ_CHAT_MODEL,
        "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE
    }