"""
Query API endpoints for the Legal RAG System
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

from embeddings.embed_client import embedding_client
from vectordb.pinecone_client import query_embeddings
from llm_service.llm_client import llm_client
from utils.validation import validation_utils
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["Legal Document Q&A"])

@router.post("/ask")
async def ask_legal_question(
    question: str = Query(..., description="Legal question to ask"),
    top_k: int = Query(5, description="Number of results to retrieve"),
    similarity_threshold: float = Query(0.7, description="Similarity threshold for results"),
    doc_filter: Optional[str] = Query(None, description="Filter by document ID"),
    doc_type_filter: Optional[str] = Query(None, description="Filter by document type")
):
    """
    Ask a legal question and get an AI-generated answer based on document context
    """
    try:
        # Validate query
        validation_result = validation_utils.validate_query(question)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation_result["errors"], "warnings": validation_result["warnings"]}
            )
        
        # Validate search parameters
        param_validation = validation_utils.validate_search_parameters(top_k, similarity_threshold)
        if not param_validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={"errors": param_validation["errors"]}
            )
        
        cleaned_params = param_validation["cleaned_params"]
        top_k = cleaned_params.get("top_k", top_k)
        similarity_threshold = cleaned_params.get("similarity_threshold", similarity_threshold)
        
        # Generate query embedding
        query_embedding = embedding_client.get_single_embedding(validation_result["cleaned_query"])
        
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")
        
        # Build filter
        filter_dict = {}
        if doc_filter:
            filter_dict["doc_id"] = doc_filter
        if doc_type_filter:
            filter_dict["doc_type"] = doc_type_filter
        
        # Query vector database
        search_results = query_embeddings(
            query_vector=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict if filter_dict else None
        )
        
        # Filter by similarity threshold
        filtered_results = []
        for match in search_results.get('matches', []):
            if match.get('score', 0) >= similarity_threshold:
                filtered_results.append(match)
        
        if not filtered_results:
            return {
                "answer": "I couldn't find relevant information in the legal documents to answer your question. Please try rephrasing your question or check if the relevant documents have been uploaded.",
                "sources": [],
                "confidence": 0.0,
                "warnings": validation_result.get("warnings", [])
            }
        
        # Generate answer using LLM
        answer = llm_client.generate_legal_response(
            question=validation_result["cleaned_query"],
            context_chunks=filtered_results
        )
        
        # Calculate confidence based on similarity scores
        confidence = sum(match.get('score', 0) for match in filtered_results) / len(filtered_results)
        
        # Format sources
        sources = []
        for match in filtered_results:
            metadata = match.get('metadata', {})
            sources.append({
                "doc_id": metadata.get('doc_id', ''),
                "doc_title": metadata.get('doc_title', ''),
                "section_title": metadata.get('section_title', ''),
                "similarity_score": match.get('score', 0),
                "chunk_text": metadata.get('text', '')[:200] + "..."  # Truncate for display
            })
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "total_sources": len(sources),
            "warnings": validation_result.get("warnings", [])
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_documents(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(10, description="Number of results to return"),
    doc_filter: Optional[str] = Query(None, description="Filter by document ID")
):
    """
    Search for relevant document chunks without generating an answer
    """
    try:
        # Validate query
        validation_result = validation_utils.validate_query(query)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation_result["errors"]}
            )
        
        # Generate query embedding
        query_embedding = embedding_client.get_single_embedding(validation_result["cleaned_query"])
        
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")
        
        # Build filter
        filter_dict = {"doc_id": doc_filter} if doc_filter else None
        
        # Query vector database
        search_results = query_embeddings(
            query_vector=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        # Format results
        results = []
        for match in search_results.get('matches', []):
            metadata = match.get('metadata', {})
            results.append({
                "doc_id": metadata.get('doc_id', ''),
                "doc_title": metadata.get('doc_title', ''),
                "section_title": metadata.get('section_title', ''),
                "similarity_score": match.get('score', 0),
                "text": metadata.get('text', ''),
                "word_count": metadata.get('word_count', 0),
                "legal_density": metadata.get('legal_density', 0)
            })
        
        return {
            "query": validation_result["cleaned_query"],
            "results": results,
            "total_results": len(results),
            "warnings": validation_result.get("warnings", [])
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggest")
async def suggest_questions():
    """
    Get suggested legal questions for testing
    """
    suggestions = [
        "What is the employee's base salary?",
        "What are the termination provisions?",
        "What is the non-competition period?",
        "What are the confidentiality obligations?",
        "What governing law applies to this contract?",
        "What are the intellectual property provisions?",
        "What is the definition of confidential information?",
        "What remedies are available for breach?",
        "What are the key parties in this agreement?",
        "What is the effective date of this agreement?"
    ]
    
    return {
        "suggestions": suggestions,
        "total_suggestions": len(suggestions)
    }