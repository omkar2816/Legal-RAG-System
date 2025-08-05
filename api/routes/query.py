"""
Query API endpoints for the Legal RAG System
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
import logging

from api.auth import get_current_user
from config.settings import settings

from embeddings.embed_client import embedding_client
from vectordb.pinecone_client import query_embeddings
from vectordb.advanced_retrieval import retrieve_documents_advanced, analyze_query_intent
from llm_service.llm_client import llm_client
from llm_service.response_formatter import response_formatter
from llm_service.response_schema import ResponseFormatter, ResponseSchemaValidator
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
    doc_type_filter: Optional[str] = Query(None, description="Filter by document type"),
    current_user: Dict[str, Any] = Depends(get_current_user) if settings.ENABLE_AUTH else None
):
    """
    Ask a legal question and get an AI-generated answer based on document context
    
    Returns:
        Enhanced structured response with comprehensive metadata
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
        
        # Use hybrid retrieval for better accuracy
        if settings.ENABLE_HYBRID_SEARCH:
            from vectordb.hybrid_retrieval import multi_stage_retrieval
            advanced_results = multi_stage_retrieval(
                query=validation_result["cleaned_query"],
                top_k=top_k,
                filter_dict=filter_dict if filter_dict else None
            )
        else:
            # Fallback to advanced retrieval
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
        llm_response = llm_client.generate_legal_response(
            question=validation_result["cleaned_query"],
            context_chunks=filtered_results
        )
        
        # Handle both old string responses and new structured responses
        if isinstance(llm_response, dict):
            # New structured response
            answer = llm_response.get("answer", "")
            confidence_scores = llm_response.get("confidence_scores", [])
            overall_confidence = llm_response.get("overall_confidence", 0.0)
            clause_references = llm_response.get("clause_references", [])
            source_clause_ref = llm_response.get("source_clause_ref", [])
            metadata = llm_response.get("metadata", {})
            
            # Calculate confidence based on structured data
            confidence = overall_confidence if overall_confidence > 0 else (
                sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            )
            
            # Create structured data for formatter
            structured_data = {
                "questions": llm_response.get("questions", [validation_result["cleaned_query"]]),
                "confidence_scores": confidence_scores,
                "overall_confidence": overall_confidence,
                "clause_references": clause_references,
                "source_clause_ref": source_clause_ref,
                "context_chunks_used": llm_response.get("context_chunks_used", len(filtered_results)),
                "metadata": metadata
            }
        else:
            # Legacy string response
            answer = llm_response
            confidence = sum(match.get('score', 0) for match in filtered_results) / len(filtered_results)
            structured_data = None
        
        # Get the effective threshold used (from the first result)
        threshold_used = advanced_results[0].get('threshold_used', similarity_threshold) if advanced_results else similarity_threshold
        
        # Format the complete response using the enhanced response formatter
        formatted_response = response_formatter.format_response(
            answer=answer,
            sources=advanced_results,
            confidence=confidence,
            query=validation_result["cleaned_query"],
            threshold_used=threshold_used,
            structured_data=structured_data
        )
        
        # Validate the response structure
        validation_result = ResponseSchemaValidator.validate_response(formatted_response)
        if not validation_result["valid"]:
            logger.warning(f"Response validation warnings: {validation_result['warnings']}")
        
        return formatted_response
        
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
    
    Returns:
        Enhanced search results with comprehensive metadata
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
                "chunk_id": result.get('chunk_id', ''),
                "has_citations": any(word in result.get('text', '').lower() for word in ["clause", "section", "page", "according"]),
                "text_preview": result.get('text', '')[:150] + "..." if len(result.get('text', '')) > 150 else result.get('text', '')
            }
            
            # Add keyword anchoring information if available
            if result.get('retrieval_method') == 'keyword_anchoring':
                result_info.update({
                    "retrieval_method": "keyword_anchoring",
                    "keyword_matches": result.get('keyword_matches', [])
                })
            else:
                result_info["retrieval_method"] = "semantic_search"
            
            # Add clause identifiers if available
            if result.get('clause_identifiers'):
                result_info["clause_identifiers"] = result.get('clause_identifiers')
            
            results.append(result_info)
        
        # Create enhanced search response
        search_response = {
            "query": {
                "original": query,
                "processed": validation_result["cleaned_query"],
                "language": "en",
                "intent": {
                    "primary_intent": "search",
                    "all_intents": ["search"],
                    "complexity": "low"
                }
            },
            "results": results,
            "total_results": len(results),
            "search_metadata": {
                "threshold_used": 0.25,
                "adaptive_threshold": True,
                "retrieval_method": "semantic_search",
                "coverage": {
                    "documents": len(set(r.get("doc_id", "") for r in results)),
                    "pages": len(set(r.get("page_number", -1) for r in results if r.get("page_number", -1) != -1)),
                    "sections": len(set(r.get("section_title", "") for r in results if r.get("section_title")))
                }
            },
            "warnings": validation_result.get("warnings", []),
            "recommendations": []
        }
        
        # Add recommendations based on results
        if len(results) < 3:
            search_response["recommendations"].append({
                "type": "expand_search",
                "priority": "medium",
                "suggestion": "Consider broadening your search terms",
                "examples": ["Try synonyms", "Use more general terms"]
            })
        
        if len(set(r.get("doc_id", "") for r in results)) < 2:
            search_response["recommendations"].append({
                "type": "add_documents",
                "priority": "medium",
                "suggestion": "Upload additional policy documents",
                "examples": ["Policy schedules", "Endorsements", "Riders"]
            })
        
        return search_response
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze")
async def analyze_query(query: str = Query(..., description="Query to analyze")):
    """
    Analyze the intent and legal category of a query
    
    Returns:
        Enhanced query analysis with detailed metadata
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
        
        # Create enhanced analysis response
        analysis_response = {
            "query": {
                "original": query,
                "processed": validation_result["cleaned_query"],
                "language": "en",
                "intent": {
                    "primary_intent": intent_analysis.get("primary_intent", "general"),
                    "all_intents": intent_analysis.get("all_intents", []),
                    "complexity": intent_analysis.get("complexity", "low")
                }
            },
            "analysis": {
                "intent_analysis": intent_analysis,
                "complexity_score": {
                    "word_count": len(query.split()),
                    "has_multiple_clauses": query.count(',') > 0 or query.count('and') > 0 or query.count('or') > 0,
                    "has_technical_terms": any(term in query.lower() for term in ["clause", "section", "policy", "coverage", "exclusion"]),
                    "complexity_level": "high" if len(query.split()) > 10 else "medium" if len(query.split()) > 5 else "low"
                },
                "legal_category": intent_analysis.get("legal_category", "general"),
                "suggested_response_type": intent_analysis.get("suggested_response_type", "general")
            },
            "warnings": validation_result.get("warnings", []),
            "recommendations": []
        }
        
        # Add recommendations based on analysis
        if len(query.split()) < 3:
            analysis_response["recommendations"].append({
                "type": "expand_query",
                "priority": "medium",
                "suggestion": "Consider adding more specific terms to your query",
                "examples": ["Include policy section numbers", "Add specific legal terms"]
            })
        
        if intent_analysis.get("complexity") == "high":
            analysis_response["recommendations"].append({
                "type": "simplify_query",
                "priority": "low",
                "suggestion": "Consider breaking down complex queries into simpler ones",
                "examples": ["Ask one question at a time", "Use shorter, more focused queries"]
            })
        
        return analysis_response
        
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggest")
async def suggest_questions():
    """
    Get suggested legal questions for testing
    
    Returns:
        Enhanced suggestions with categorization and metadata
    """
    suggestions = [
        {
            "question": "What are the pre-existing disease exclusions?",
            "category": "exclusion",
            "complexity": "medium",
            "expected_response_type": "exclusion"
        },
        {
            "question": "What is the coverage limit for hospitalization?",
            "category": "coverage",
            "complexity": "medium",
            "expected_response_type": "coverage"
        },
        {
            "question": "How do I file a claim?",
            "category": "procedure",
            "complexity": "low",
            "expected_response_type": "procedural"
        },
        {
            "question": "What is the waiting period for coverage?",
            "category": "timing",
            "complexity": "low",
            "expected_response_type": "waiting_period"
        },
        {
            "question": "What are the premium payment terms?",
            "category": "financial",
            "complexity": "medium",
            "expected_response_type": "premium"
        },
        {
            "question": "What happens if I miss a premium payment?",
            "category": "financial",
            "complexity": "medium",
            "expected_response_type": "premium"
        },
        {
            "question": "What is the deductible amount?",
            "category": "financial",
            "complexity": "low",
            "expected_response_type": "coverage"
        },
        {
            "question": "What are the renewal terms?",
            "category": "renewal",
            "complexity": "medium",
            "expected_response_type": "renewal"
        },
        {
            "question": "What is the termination process?",
            "category": "termination",
            "complexity": "medium",
            "expected_response_type": "termination"
        },
        {
            "question": "What medical expenses are covered?",
            "category": "coverage",
            "complexity": "medium",
            "expected_response_type": "coverage"
        }
    ]
    
    return {
        "suggestions": suggestions,
        "total_suggestions": len(suggestions),
        "categories": list(set(s["category"] for s in suggestions)),
        "complexity_levels": list(set(s["complexity"] for s in suggestions)),
        "metadata": {
            "purpose": "testing_and_demo",
            "coverage": "comprehensive",
            "last_updated": "2024-01-01"
        }
    }