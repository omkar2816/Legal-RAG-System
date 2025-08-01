"""
Enhanced Response Schema for Legal RAG System
Defines structured response format with comprehensive metadata and validation
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

class ResponseType(Enum):
    """Types of legal responses"""
    DIRECT_ANSWER = "direct_answer"
    PROCEDURAL = "procedural"
    EXCLUSION = "exclusion"
    COVERAGE = "coverage"
    CLAIM = "claim"
    WAITING_PERIOD = "waiting_period"
    PREMIUM = "premium"
    RENEWAL = "renewal"
    TERMINATION = "termination"
    LIMITATION = "limitation"
    GENERAL = "general"
    ERROR = "error"
    NO_RESULTS = "no_results"

class ConfidenceLevel(Enum):
    """Confidence levels for responses"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"

class WarningSeverity(Enum):
    """Warning severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class QueryInfo:
    """Query information structure"""
    original: str
    processed: str
    language: str = "en"
    intent: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConfidenceInfo:
    """Confidence information structure"""
    score: float
    level: str
    breakdown: Dict[str, float] = field(default_factory=dict)

@dataclass
class SourceInfo:
    """Source information structure"""
    doc_id: str
    doc_title: str
    section_title: str
    similarity_score: float
    threshold_used: float
    retrieval_method: str
    page_number: int
    chunk_id: str
    text_preview: str
    has_citations: bool
    word_count: int
    legal_density: float
    structural_rank: int
    keyword_matches: Optional[List[str]] = None
    clause_identifiers: Optional[List[str]] = None

@dataclass
class SourcesInfo:
    """Sources information structure"""
    total_count: int
    documents: List[SourceInfo]
    coverage: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SearchParameters:
    """Search parameters structure"""
    threshold_used: float
    adaptive_threshold: bool
    retrieval_method: str

@dataclass
class QualityIndicators:
    """Quality indicators structure"""
    completeness: float
    specificity: float
    citation_count: int

@dataclass
class Warning:
    """Warning structure"""
    type: str
    severity: str
    message: str
    suggestion: str

@dataclass
class Recommendation:
    """Recommendation structure"""
    type: str
    priority: str
    suggestion: str
    examples: List[str] = field(default_factory=list)

@dataclass
class EnhancedMetadata:
    """Enhanced metadata structure"""
    questions: List[str]
    confidence_scores: List[float]
    overall_confidence: float
    clause_references: List[Dict[str, Any]]
    source_clause_ref: List[Dict[str, Any]]
    context_chunks_used: int
    metadata: Dict[str, Any]
    response_analysis: Dict[str, Any]

@dataclass
class ExplainabilityInfo:
    """Explainability information structure"""
    query_analysis: Dict[str, Any]
    source_analysis: Dict[str, Any]
    response_quality: Dict[str, Any]
    audit_trail: Dict[str, Any]

@dataclass
class StructuredResponse:
    """Complete structured response"""
    response_id: str
    timestamp: Optional[str]
    answer: str
    response_type: str
    category: str
    query: QueryInfo
    confidence: ConfidenceInfo
    sources: SourcesInfo
    search_parameters: SearchParameters
    quality_indicators: QualityIndicators
    warnings: List[Warning]
    recommendations: List[Recommendation]
    enhanced_metadata: Optional[EnhancedMetadata] = None
    explainability: Optional[ExplainabilityInfo] = None

class ResponseSchemaValidator:
    """Validator for structured responses"""
    
    @staticmethod
    def validate_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean response structure"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = [
            "response_id", "answer", "response_type", "category",
            "query", "confidence", "sources", "search_parameters",
            "quality_indicators", "warnings", "recommendations"
        ]
        
        for field in required_fields:
            if field not in response:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
        
        # Validate confidence score
        if "confidence" in response:
            confidence = response["confidence"]
            if isinstance(confidence, dict) and "score" in confidence:
                score = confidence["score"]
                if not isinstance(score, (int, float)) or score < 0 or score > 1:
                    validation_result["warnings"].append("Confidence score should be between 0 and 1")
        
        # Validate sources
        if "sources" in response:
            sources = response["sources"]
            if isinstance(sources, dict) and "total_count" in sources:
                total_count = sources["total_count"]
                if not isinstance(total_count, int) or total_count < 0:
                    validation_result["warnings"].append("Total count should be a non-negative integer")
        
        return validation_result
    
    @staticmethod
    def format_response_for_api(response: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for API output"""
        # Ensure all nested objects are properly serialized
        formatted = response.copy()
        
        # Convert dataclass objects to dictionaries if present
        for key, value in formatted.items():
            if hasattr(value, '__dict__'):
                formatted[key] = value.__dict__
            elif isinstance(value, list):
                formatted[key] = [
                    item.__dict__ if hasattr(item, '__dict__') else item 
                    for item in value
                ]
        
        return formatted

class ResponseFormatter:
    """Utility class for formatting responses"""
    
    @staticmethod
    def create_success_response(
        answer: str,
        sources: List[Dict[str, Any]],
        confidence: float,
        query: str,
        threshold_used: float,
        response_type: str = "general",
        category: str = "general"
    ) -> Dict[str, Any]:
        """Create a structured success response"""
        
        # Generate response ID
        import uuid
        response_id = f"resp_{uuid.uuid4().hex[:8]}"
        
        # Create query info
        query_info = QueryInfo(
            original=query,
            processed=query,
            language="en",
            intent={"primary_intent": "general", "all_intents": [], "complexity": "low"}
        )
        
        # Create confidence info
        confidence_level = "high" if confidence >= 0.8 else "medium" if confidence >= 0.6 else "low" if confidence >= 0.4 else "very_low"
        confidence_info = ConfidenceInfo(
            score=round(confidence, 3),
            level=confidence_level,
            breakdown={
                "overall": confidence,
                "source_relevance": sum(s.get('similarity_score', 0) for s in sources) / len(sources) if sources else 0,
                "response_completeness": 0.8,  # Placeholder
                "citation_quality": 0.7  # Placeholder
            }
        )
        
        # Create sources info
        source_objects = []
        for source in sources:
            source_obj = SourceInfo(
                doc_id=source.get("doc_id", ""),
                doc_title=source.get("doc_title", ""),
                section_title=source.get("section_title", ""),
                similarity_score=round(source.get("similarity_score", 0), 4),
                threshold_used=round(threshold_used, 4),
                retrieval_method=source.get("retrieval_method", "semantic_search"),
                page_number=source.get("page_number", -1),
                chunk_id=source.get("chunk_id", ""),
                text_preview=source.get("text", "")[:150] + "..." if len(source.get("text", "")) > 150 else source.get("text", ""),
                has_citations=any(word in source.get("text", "").lower() for word in ["clause", "section", "page"]),
                word_count=source.get("word_count", 0),
                legal_density=source.get("legal_density", 0),
                structural_rank=source.get("structural_rank", 3)
            )
            source_objects.append(source_obj)
        
        sources_info = SourcesInfo(
            total_count=len(source_objects),
            documents=source_objects,
            coverage={
                "documents": len(set(s.doc_id for s in source_objects)),
                "pages": len(set(s.page_number for s in source_objects if s.page_number != -1)),
                "sections": len(set(s.section_title for s in source_objects if s.section_title)),
                "total_chunks": len(source_objects)
            }
        )
        
        # Create search parameters
        search_params = SearchParameters(
            threshold_used=round(threshold_used, 4),
            adaptive_threshold=True,
            retrieval_method="semantic_search"
        )
        
        # Create quality indicators
        quality_indicators = QualityIndicators(
            completeness=0.8,  # Placeholder
            specificity=0.7,   # Placeholder
            citation_count=len([s for s in source_objects if s.has_citations])
        )
        
        # Create warnings and recommendations
        warnings = []
        recommendations = []
        
        if confidence < 0.5:
            warnings.append(Warning(
                type="low_confidence",
                severity="high",
                message="Low confidence response - consider rephrasing your question",
                suggestion="Try using more specific terms or breaking down your question"
            ))
        
        if len(source_objects) < 2:
            recommendations.append(Recommendation(
                type="add_documents",
                priority="medium",
                suggestion="Upload additional policy documents for better coverage",
                examples=["Policy schedules", "Endorsements", "Riders"]
            ))
        
        # Create structured response
        structured_response = StructuredResponse(
            response_id=response_id,
            timestamp=datetime.utcnow().isoformat(),
            answer=answer,
            response_type=response_type,
            category=category,
            query=query_info,
            confidence=confidence_info,
            sources=sources_info,
            search_parameters=search_params,
            quality_indicators=quality_indicators,
            warnings=[w.__dict__ for w in warnings],
            recommendations=[r.__dict__ for r in recommendations]
        )
        
        return ResponseSchemaValidator.format_response_for_api(structured_response.__dict__)
    
    @staticmethod
    def create_error_response(error: str, query: str) -> Dict[str, Any]:
        """Create a structured error response"""
        import uuid
        
        return {
            "response_id": f"resp_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.utcnow().isoformat(),
            "answer": "I apologize, but I encountered an error while processing your query. Please try rephrasing your question or contact support if the issue persists.",
            "response_type": "error",
            "category": "error",
            "query": {
                "original": query,
                "processed": query,
                "language": "en",
                "intent": {"primary_intent": "error", "all_intents": [], "complexity": "unknown"}
            },
            "confidence": {
                "score": 0.0,
                "level": "very_low",
                "breakdown": {"overall": 0.0, "source_relevance": 0.0, "response_completeness": 0.0, "citation_quality": 0.0}
            },
            "sources": {
                "total_count": 0,
                "documents": [],
                "coverage": {"documents": 0, "pages": 0, "sections": 0, "total_chunks": 0}
            },
            "search_parameters": {
                "threshold_used": 0.0,
                "adaptive_threshold": False,
                "retrieval_method": "none"
            },
            "quality_indicators": {
                "completeness": 0.0,
                "specificity": 0.0,
                "citation_count": 0
            },
            "error": {
                "type": "processing_error",
                "message": error,
                "severity": "high"
            },
            "warnings": [{
                "type": "technical_error",
                "severity": "high",
                "message": "Technical error occurred during processing",
                "suggestion": "Try again or contact support"
            }],
            "recommendations": [{
                "type": "retry_query",
                "priority": "high",
                "suggestion": "Try rephrasing your question",
                "examples": ["Use simpler language", "Break down complex questions"]
            }]
        }

# Export the main classes
__all__ = [
    'ResponseType',
    'ConfidenceLevel', 
    'WarningSeverity',
    'QueryInfo',
    'ConfidenceInfo',
    'SourceInfo',
    'SourcesInfo',
    'SearchParameters',
    'QualityIndicators',
    'Warning',
    'Recommendation',
    'EnhancedMetadata',
    'ExplainabilityInfo',
    'StructuredResponse',
    'ResponseSchemaValidator',
    'ResponseFormatter'
] 