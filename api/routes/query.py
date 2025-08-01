"""
Query API endpoints for the Legal RAG System
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

from embeddings.embed_client import embedding_client
from vectordb.pinecone_client import query_embeddings
from vectordb.advanced_retrieval import retrieve_documents_advanced, analyze_query_intent
from llm_service.llm_client import llm_client
from llm_service.response_formatter import response_formatter
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
        
        # Build filter
        filter_dict = {}
        if doc_filter:
            filter_dict["doc_id"] = doc_filter
        if doc_type_filter:
            filter_dict["doc_type"] = doc_type_filter
        
        # Use advanced retrieval with enhanced threshold handling
        advanced_results = retrieve_documents_advanced(
            query=validation_result["cleaned_query"],
            top_k=top_k,
            threshold=similarity_threshold,
            filter_dict=filter_dict if filter_dict else None,
            return_count=top_k,
            adaptive_threshold=settings.ADAPTIVE_THRESHOLD
        )
        
        # Convert advanced results to the format expected by LLM client
        filtered_results = []
        for result in advanced_results:
            # Create a match-like structure for LLM client compatibility
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
            return response_formatter.format_no_results_response(
                query=validation_result["cleaned_query"],
                threshold=similarity_threshold
            )
        
        # Generate answer using LLM
        answer = llm_client.generate_legal_response(
            question=validation_result["cleaned_query"],
            context_chunks=filtered_results
        )
        
        # Calculate confidence based on similarity scores
        confidence = sum(match.get('score', 0) for match in filtered_results) / len(filtered_results)
        
        # Get the effective threshold used (from the first result)
        threshold_used = advanced_results[0].get('threshold_used', similarity_threshold) if advanced_results else similarity_threshold
        
        # Format the complete response using the response formatter
        return response_formatter.format_response(
            answer=answer,
            sources=advanced_results,
            confidence=confidence,
            query=validation_result["cleaned_query"],
            threshold_used=threshold_used
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return response_formatter.format_error_response(
            error=str(e),
            query=question
        )

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
        
        # Build filter
        filter_dict = {"doc_id": doc_filter} if doc_filter else None
        
        # Use advanced retrieval with enhanced threshold handling
        advanced_results = retrieve_documents_advanced(
            query=validation_result["cleaned_query"],
            top_k=top_k,
            threshold=0.25,  # Lower threshold for search endpoint
            filter_dict=filter_dict,
            return_count=top_k,
            adaptive_threshold=settings.ADAPTIVE_THRESHOLD
        )
        
        # Format results with enhanced threshold and keyword anchoring information
        results = []
        for result in advanced_results:
            result_info = {
                "doc_id": result.get('doc_id', ''),
                "doc_title": result.get('doc_title', ''),
                "section_title": result.get('section_title', ''),
                "similarity_score": result.get('similarity_score', 0),
                "structural_rank": result.get('structural_rank', 3),
                "threshold_used": result.get('threshold_used', 0.25),
                "text": result.get('text', ''),
                "word_count": result.get('word_count', 0),
                "legal_density": result.get('legal_density', 0),
                "page_number": result.get('page_number', -1),
                "chunk_id": result.get('chunk_id', '')
            }
            
            # Add keyword anchoring information if available
            if result.get('retrieval_method') == 'keyword_anchoring':
                result_info.update({
                    "retrieval_method": "keyword_anchoring",
                    "keyword_matches": result.get('keyword_matches', [])
                })
            else:
                result_info["retrieval_method"] = "semantic_search"
            
            results.append(result_info)
        
        return {
            "query": validation_result["cleaned_query"],
            "results": results,
            "total_results": len(results),
            "warnings": validation_result.get("warnings", [])
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze")
async def analyze_query(query: str = Query(..., description="Query to analyze")):
    """
    Analyze the intent and legal category of a query
    """
    try:
        # Validate query
        validation_result = validation_utils.validate_query(query)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail={"errors": validation_result["errors"]}
            )
        
        # Analyze query intent
        intent_analysis = analyze_query_intent(query)
        
        return {
            "query": query,
            "normalized_query": validation_result["cleaned_query"],
            "intent_analysis": intent_analysis,
            "warnings": validation_result.get("warnings", [])
        }
        
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggest")
async def suggest_questions():
    """
    Get suggested legal questions for testing
    """
    suggestions = [
        "What are the pre-existing disease exclusions?",
        "What is the coverage limit for hospitalization?",
        "How do I file a claim?",
        "What is the waiting period for coverage?",
        "What are the premium payment terms?",
        "What happens if I miss a premium payment?",
        "What is the deductible amount?",
        "What are the renewal terms?",
        "What is the termination process?",
        "What medical expenses are covered?"
    ]
    
    return {
        "suggestions": suggestions,
        "total_suggestions": len(suggestions)
    }