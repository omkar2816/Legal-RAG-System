"""
Enhanced Response Formatter for Legal RAG System
Provides structured, comprehensive responses with detailed metadata and categorization
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    """Types of legal responses with enhanced categorization"""
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

@dataclass
class ResponseConfig:
    """Enhanced configuration for response formatting"""
    max_length: int = 8000
    min_length: int = 50
    include_sources: bool = True
    include_confidence: bool = True
    include_threshold_info: bool = True
    include_metadata: bool = True
    include_explainability: bool = True
    format_type: str = "enhanced_structured"
    include_timestamps: bool = True
    include_response_id: bool = True

class EnhancedLegalResponseFormatter:
    """
    Enhanced formatter for legal responses with comprehensive structure and metadata
    """
    
    def __init__(self, config: Optional[ResponseConfig] = None):
        self.config = config or ResponseConfig()
        self.response_templates = {
            ResponseType.DIRECT_ANSWER: {
                "template": "Based on the policy document: {answer}",
                "max_length": 8000,
                "category": "information"
            },
            ResponseType.PROCEDURAL: {
                "template": "According to the policy procedures: {answer}",
                "max_length": 8000,
                "category": "procedure"
            },
            ResponseType.EXCLUSION: {
                "template": "Important exclusion information: {answer}",
                "max_length": 8000,
                "category": "exclusion"
            },
            ResponseType.COVERAGE: {
                "template": "Coverage details: {answer}",
                "max_length": 8000,
                "category": "coverage"
            },
            ResponseType.CLAIM: {
                "template": "Claim process information: {answer}",
                "max_length": 8000,
                "category": "claim"
            },
            ResponseType.WAITING_PERIOD: {
                "template": "Waiting period information: {answer}",
                "max_length": 8000,
                "category": "timing"
            },
            ResponseType.PREMIUM: {
                "template": "Premium-related information: {answer}",
                "max_length": 8000,
                "category": "financial"
            },
            ResponseType.RENEWAL: {
                "template": "Renewal information: {answer}",
                "max_length": 8000,
                "category": "renewal"
            },
            ResponseType.TERMINATION: {
                "template": "Termination details: {answer}",
                "max_length": 8000,
                "category": "termination"
            },
            ResponseType.LIMITATION: {
                "template": "Limitation information: {answer}",
                "max_length": 8000,
                "category": "limitation"
            },
            ResponseType.GENERAL: {
                "template": "{answer}",
                "max_length": 8000,
                "category": "general"
            }
        }
    
    def format_response(
        self,
        answer: str,
        sources: List[Dict[str, Any]],
        confidence: float,
        query: str,
        threshold_used: float,
        structured_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Format a complete enhanced response with comprehensive structure
        
        Args:
            answer: Raw answer from LLM
            sources: List of source documents
            confidence: Confidence score
            query: Original query
            threshold_used: Threshold used for filtering
            structured_data: Enhanced structured data from LLM client
        
        Returns:
            Enhanced formatted response dictionary
        """
        # Generate response ID
        response_id = self._generate_response_id()
        
        # Determine response type and category
        response_type = self._classify_response_type(query, answer)
        category = self.response_templates[response_type]["category"]
        
        # Clean and format the answer
        formatted_answer = self._format_answer(answer, response_type)
        
        # Apply length constraints
        formatted_answer = self._apply_length_constraints(formatted_answer, response_type)
        
        # Format sources with enhanced metadata
        formatted_sources = self._format_sources(sources, threshold_used)
        
        # Determine confidence level
        confidence_level = self._determine_confidence_level(confidence)
        
        # Create comprehensive response structure
        response = {
            # Core response data
            "response_id": response_id,
            "timestamp": datetime.utcnow().isoformat() if self.config.include_timestamps else None,
            "answer": formatted_answer,
            "response_type": response_type.value,
            "category": category,
            
            # Query information
            "query": {
                "original": query,
                "processed": query,
                "language": "en",
                "intent": self._analyze_query_intent(query)
            },
            
            # Confidence and quality metrics
            "confidence": {
                "score": self._format_confidence(confidence),
                "level": confidence_level.value,
                "breakdown": self._generate_confidence_breakdown(confidence, sources, structured_data)
            },
            
            # Source information
            "sources": {
                "total_count": len(formatted_sources),
                "documents": formatted_sources,
                "coverage": self._calculate_source_coverage(formatted_sources)
            },
            
            # Search parameters
            "search_parameters": {
                "threshold_used": round(threshold_used, 4),
                "adaptive_threshold": True,
                "retrieval_method": self._determine_retrieval_method(sources)
            },
            
            # Quality indicators
            "quality_indicators": {
                "completeness": self._calculate_completeness_score(formatted_answer),
                "specificity": self._calculate_specificity_score(formatted_answer),
                "citation_count": len([s for s in formatted_sources if s.get("has_citations", False)])
            },
            
            # Warnings and recommendations
            "warnings": self._generate_enhanced_warnings(confidence, threshold_used, len(formatted_sources), formatted_answer),
            "recommendations": self._generate_recommendations(query, confidence, len(formatted_sources))
        }
        
        # Add enhanced structured data if available
        if structured_data and self.config.include_metadata:
            response["enhanced_metadata"] = {
                "questions": structured_data.get("questions", [query]),
                "confidence_scores": structured_data.get("confidence_scores", [confidence]),
                "overall_confidence": structured_data.get("overall_confidence", confidence),
                "clause_references": structured_data.get("clause_references", []),
                "source_clause_ref": structured_data.get("source_clause_ref", []),
                "context_chunks_used": structured_data.get("context_chunks_used", len(sources)),
                "metadata": structured_data.get("metadata", {}),
                "response_analysis": self._analyze_response_content(formatted_answer)
            }
        
        # Add explainability information
        if self.config.include_explainability:
            response["explainability"] = self._generate_explainability_info(structured_data, formatted_sources, query)
        
        return response
    
    def _generate_response_id(self) -> str:
        """Generate a unique response ID"""
        import uuid
        return f"resp_{uuid.uuid4().hex[:8]}"
    
    def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze the intent of the query"""
        query_lower = query.lower()
        
        intent_indicators = {
            "information_seeking": ["what", "how", "when", "where", "why", "which"],
            "procedural": ["how to", "process", "procedure", "steps", "submit", "file"],
            "coverage": ["covered", "coverage", "benefits", "what is covered"],
            "exclusion": ["excluded", "not covered", "exclusion", "limitation"],
            "financial": ["premium", "cost", "payment", "deductible", "amount"],
            "temporal": ["waiting period", "wait period", "duration", "time"],
            "claim": ["claim", "claiming", "claim process", "reimbursement"]
        }
        
        detected_intents = []
        for intent, indicators in intent_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                detected_intents.append(intent)
        
        return {
            "primary_intent": detected_intents[0] if detected_intents else "general",
            "all_intents": detected_intents,
            "complexity": "high" if len(detected_intents) > 1 else "low"
        }
    
    def _determine_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determine confidence level based on score"""
        if confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _generate_confidence_breakdown(self, confidence: float, sources: List[Dict[str, Any]], structured_data: Dict[str, Any] = None) -> Dict[str, float]:
        """Generate detailed confidence breakdown"""
        breakdown = {
            "overall": confidence,
            "source_relevance": sum(s.get('similarity_score', 0) for s in sources) / len(sources) if sources else 0,
            "response_completeness": self._calculate_completeness_score("") if not structured_data else structured_data.get("metadata", {}).get("completeness", 0),
            "citation_quality": len([s for s in sources if s.get("has_citations", False)]) / len(sources) if sources else 0
        }
        
        if structured_data:
            breakdown.update({
                "context_relevance": structured_data.get("metadata", {}).get("context_relevance", 0),
                "clause_citations": len(structured_data.get("clause_references", [])) / max(len(sources), 1)
            })
        
        return {k: round(v, 3) for k, v in breakdown.items()}
    
    def _calculate_source_coverage(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate source coverage metrics"""
        if not sources:
            return {"documents": 0, "pages": 0, "sections": 0}
        
        unique_docs = set(s.get("doc_id", "") for s in sources)
        unique_pages = set(s.get("page_number", -1) for s in sources)
        unique_sections = set(s.get("section_title", "") for s in sources)
        
        return {
            "documents": len(unique_docs),
            "pages": len([p for p in unique_pages if p != -1]),
            "sections": len([s for s in unique_sections if s]),
            "total_chunks": len(sources)
        }
    
    def _determine_retrieval_method(self, sources: List[Dict[str, Any]]) -> str:
        """Determine the primary retrieval method used"""
        methods = [s.get("retrieval_method", "semantic_search") for s in sources]
        if not methods:
            return "semantic_search"
        
        # Return the most common method
        from collections import Counter
        method_counts = Counter(methods)
        return method_counts.most_common(1)[0][0]
    
    def _calculate_completeness_score(self, answer: str) -> float:
        """Calculate response completeness score"""
        if not answer:
            return 0.0
        
        indicators = [
            len(answer) > 100,  # Minimum length
            any(word in answer.lower() for word in ["according", "clause", "section", "page", "policy"]),  # Citations
            answer.count(".") > 2,  # Multiple sentences
            not answer.endswith("..."),  # Not truncated
            len(answer.split()) > 20,  # Sufficient word count
        ]
        
        return sum(indicators) / len(indicators)
    
    def _calculate_specificity_score(self, answer: str) -> float:
        """Calculate response specificity score"""
        if not answer:
            return 0.0
        
        specificity_indicators = [
            any(word in answer.lower() for word in ["specific", "exactly", "precisely", "specifically"]),
            any(word in answer.lower() for word in ["clause", "section", "article", "paragraph"]),
            any(word in answer.lower() for word in ["page", "chapter", "part"]),
            any(word in answer.lower() for word in ["according to", "as stated in", "per the policy"]),
            len(re.findall(r'\d+', answer)) > 0,  # Contains numbers
        ]
        
        return sum(specificity_indicators) / len(specificity_indicators)
    
    def _generate_enhanced_warnings(self, confidence: float, threshold: float, source_count: int, answer: str) -> List[Dict[str, Any]]:
        """Generate enhanced warnings with severity levels"""
        warnings = []
        
        if confidence < 0.5:
            warnings.append({
                "type": "low_confidence",
                "severity": "high",
                "message": "Low confidence response - consider rephrasing your question",
                "suggestion": "Try using more specific terms or breaking down your question"
            })
        
        if threshold < 0.3:
            warnings.append({
                "type": "low_threshold",
                "severity": "medium",
                "message": "Using low similarity threshold - results may be less relevant",
                "suggestion": "Consider uploading more relevant documents"
            })
        
        if source_count == 0:
            warnings.append({
                "type": "no_sources",
                "severity": "high",
                "message": "No relevant documents found - answer may be incomplete",
                "suggestion": "Upload additional policy documents or rephrase your question"
            })
        elif source_count == 1:
            warnings.append({
                "type": "limited_sources",
                "severity": "medium",
                "message": "Limited source material - consider checking additional documents",
                "suggestion": "Upload more policy documents for comprehensive coverage"
            })
        
        if len(answer) < 50:
            warnings.append({
                "type": "short_answer",
                "severity": "medium",
                "message": "Answer appears incomplete - may need more context",
                "suggestion": "Try asking a more specific question"
            })
        
        return warnings
    
    def _generate_recommendations(self, query: str, confidence: float, source_count: int) -> List[Dict[str, Any]]:
        """Generate recommendations for improving results"""
        recommendations = []
        
        if confidence < 0.7:
            recommendations.append({
                "type": "improve_query",
                "priority": "high",
                "suggestion": "Rephrase your question with more specific terms",
                "examples": ["Instead of 'coverage', try 'what medical expenses are covered'"]
            })
        
        if source_count < 2:
            recommendations.append({
                "type": "add_documents",
                "priority": "medium",
                "suggestion": "Upload additional policy documents for better coverage",
                "examples": ["Policy schedules", "Endorsements", "Riders"]
            })
        
        if "how" in query.lower() and "procedure" not in query.lower():
            recommendations.append({
                "type": "procedural_query",
                "priority": "low",
                "suggestion": "For procedural questions, include 'procedure' or 'steps' in your query",
                "examples": ["How to file a claim procedure", "Steps to renew policy"]
            })
        
        return recommendations
    
    def _analyze_response_content(self, answer: str) -> Dict[str, Any]:
        """Analyze the content of the response"""
        if not answer:
            return {"analysis": "empty_response"}
        
        analysis = {
            "word_count": len(answer.split()),
            "sentence_count": len(re.split(r'[.!?]+', answer)),
            "has_citations": any(word in answer.lower() for word in ["clause", "section", "page", "according"]),
            "has_numbers": len(re.findall(r'\d+', answer)) > 0,
            "has_bullet_points": answer.count('•') > 0 or answer.count('-') > 3,
            "tone": "professional" if any(word in answer.lower() for word in ["policy", "clause", "according"]) else "general"
        }
        
        return analysis

    def _classify_response_type(self, query: str, answer: str) -> ResponseType:
        """Classify the type of response based on query and answer content"""
        query_lower = query.lower()
        answer_lower = answer.lower()
        
        # Check for waiting period queries
        if any(term in query_lower for term in ["waiting period", "wait period", "waiting time"]):
            return ResponseType.WAITING_PERIOD
        
        # Check for premium queries
        if any(term in query_lower for term in ["premium", "payment", "cost", "amount"]):
            return ResponseType.PREMIUM
        
        # Check for renewal queries
        if any(term in query_lower for term in ["renewal", "renew", "extension"]):
            return ResponseType.RENEWAL
        
        # Check for termination queries
        if any(term in query_lower for term in ["termination", "cancel", "terminate", "end"]):
            return ResponseType.TERMINATION
        
        # Check for limitation queries
        if any(term in query_lower for term in ["limitation", "limit", "maximum", "cap"]):
            return ResponseType.LIMITATION
        
        # Check for procedural queries
        if any(term in query_lower for term in ["how to", "process", "procedure", "steps", "submit"]):
            return ResponseType.PROCEDURAL
        
        # Check for exclusion queries
        if any(term in query_lower for term in ["exclusion", "not covered", "excluded", "limitation"]):
            return ResponseType.EXCLUSION
        
        # Check for coverage queries
        if any(term in query_lower for term in ["coverage", "covered", "benefits", "what is covered"]):
            return ResponseType.COVERAGE
        
        # Check for claim queries
        if any(term in query_lower for term in ["claim", "claiming", "claim process"]):
            return ResponseType.CLAIM
        
        return ResponseType.GENERAL
    
    def _format_answer(self, answer: str, response_type: ResponseType) -> str:
        """Format the answer using appropriate template"""
        # Clean the answer
        cleaned_answer = self._clean_text(answer)
        
        # Apply template
        template = self.response_templates[response_type]["template"]
        formatted = template.format(answer=cleaned_answer)
        
        # Ensure proper sentence structure
        formatted = self._ensure_proper_sentence(formatted)
        
        return formatted
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common LLM artifacts
        text = re.sub(r'^Based on the context[:\s]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^According to the document[:\s]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^The document states[:\s]*', '', text, flags=re.IGNORECASE)
        
        # Ensure proper capitalization
        if text and not text[0].isupper():
            text = text[0].upper() + text[1:]
        
        return text
    
    def _ensure_proper_sentence(self, text: str) -> str:
        """Ensure text ends with proper punctuation"""
        if not text:
            return text
        
        # Remove trailing punctuation and add period if needed
        text = text.rstrip('.,;:!?')
        
        # Add period if it doesn't end with punctuation
        if text and not text[-1] in '.!?':
            text += '.'
        
        return text
    
    def _apply_length_constraints(self, text: str, response_type: ResponseType) -> str:
        """Apply length constraints to the answer"""
        max_length = self.response_templates[response_type]["max_length"]
        
        # If text is within limits, return as is
        if len(text) <= max_length:
            return text
        
        # Only truncate if significantly over the limit (more than 10% over)
        if len(text) > max_length * 1.1:
            # Truncate at sentence boundary
            sentences = re.split(r'[.!?]+', text)
            truncated = ""
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # Add proper punctuation
                if not sentence[-1] in '.!?':
                    sentence += '.'
                
                if len(truncated + sentence) <= max_length:
                    truncated += sentence + " "
                else:
                    break
            
            return truncated.strip()
        
        # If only slightly over, return the full text
        return text
    
    def _format_sources(self, sources: List[Dict[str, Any]], threshold_used: float) -> List[Dict[str, Any]]:
        """Format sources with enhanced metadata"""
        formatted_sources = []
        
        for source in sources:
            formatted_source = {
                "doc_id": source.get("doc_id", ""),
                "doc_title": source.get("doc_title", ""),
                "section_title": source.get("section_title", ""),
                "similarity_score": round(source.get("similarity_score", 0), 4),
                "threshold_used": round(threshold_used, 4),
                "retrieval_method": source.get("retrieval_method", "semantic_search"),
                "page_number": source.get("page_number", -1),
                "chunk_id": source.get("chunk_id", ""),
                "text_preview": self._truncate_text(source.get("text", ""), 150),
                "has_citations": self._check_for_citations(source.get("text", "")),
                "word_count": source.get("word_count", 0),
                "legal_density": source.get("legal_density", 0),
                "structural_rank": source.get("structural_rank", 3)
            }
            
            # Add keyword information if available
            if source.get("keyword_matches"):
                formatted_source["keyword_matches"] = source.get("keyword_matches")
            
            # Add clause identifiers if available
            if source.get("clause_identifiers"):
                formatted_source["clause_identifiers"] = source.get("clause_identifiers")
            
            formatted_sources.append(formatted_source)
        
        return formatted_sources
    
    def _check_for_citations(self, text: str) -> bool:
        """Check if text contains citations"""
        citation_indicators = [
            "clause", "section", "page", "article", "paragraph",
            "according to", "as stated in", "per the policy"
        ]
        return any(indicator in text.lower() for indicator in citation_indicators)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        
        # Truncate at word boundary
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # If we can find a space in the last 20%
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def _format_confidence(self, confidence: float) -> float:
        """Format confidence score"""
        return round(confidence, 3)
    
    def _generate_explainability_info(self, structured_data: Dict[str, Any], sources: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Generate comprehensive explainability information"""
        explainability = {
            "query_analysis": {
                "original_query": query,
                "intent_detected": self._analyze_query_intent(query),
                "complexity_score": self._calculate_query_complexity(query)
            },
            "source_analysis": {
                "total_sources": len(sources),
                "unique_documents": len(set(s.get("doc_id", "") for s in sources)),
                "source_quality": self._calculate_source_quality(sources),
                "coverage_analysis": self._analyze_source_coverage(sources)
            },
            "response_quality": {
                "completeness": self._calculate_completeness_score("") if not structured_data else structured_data.get("metadata", {}).get("completeness", 0),
                "specificity": self._calculate_specificity_score("") if not structured_data else 0,
                "citation_quality": len([s for s in sources if s.get("has_citations", False)]) / len(sources) if sources else 0
            },
            "audit_trail": {
                "timestamp": datetime.utcnow().isoformat(),
                "query_processed": structured_data.get("questions", [query]) if structured_data else [query],
                "confidence_scores": structured_data.get("confidence_scores", []) if structured_data else [],
                "clause_references": structured_data.get("clause_references", []) if structured_data else [],
                "source_clause_ref": structured_data.get("source_clause_ref", []) if structured_data else []
            }
        }
        
        return explainability
    
    def _calculate_query_complexity(self, query: str) -> Dict[str, Any]:
        """Calculate query complexity metrics"""
        words = query.split()
        complexity = {
            "word_count": len(words),
            "has_multiple_clauses": query.count(',') > 0 or query.count('and') > 0 or query.count('or') > 0,
            "has_technical_terms": any(term in query.lower() for term in ["clause", "section", "policy", "coverage", "exclusion"]),
            "complexity_level": "high" if len(words) > 10 else "medium" if len(words) > 5 else "low"
        }
        return complexity
    
    def _calculate_source_quality(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate source quality metrics"""
        if not sources:
            return {"average_score": 0, "quality_level": "none"}
        
        scores = [s.get("similarity_score", 0) for s in sources]
        avg_score = sum(scores) / len(scores)
        
        quality_level = "high" if avg_score > 0.8 else "medium" if avg_score > 0.6 else "low"
        
        return {
            "average_score": round(avg_score, 3),
            "quality_level": quality_level,
            "high_quality_sources": len([s for s in scores if s > 0.8]),
            "medium_quality_sources": len([s for s in scores if 0.6 <= s <= 0.8]),
            "low_quality_sources": len([s for s in scores if s < 0.6])
        }
    
    def _analyze_source_coverage(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze source coverage patterns"""
        if not sources:
            return {"coverage_type": "none", "coverage_score": 0}
        
        unique_docs = set(s.get("doc_id", "") for s in sources)
        unique_sections = set(s.get("section_title", "") for s in sources)
        
        coverage_score = min(len(unique_docs) / 3, 1.0)  # Normalize to 0-1
        
        coverage_type = "comprehensive" if len(unique_docs) > 2 else "moderate" if len(unique_docs) > 1 else "limited"
        
        return {
            "coverage_type": coverage_type,
            "coverage_score": round(coverage_score, 3),
            "documents_covered": len(unique_docs),
            "sections_covered": len(unique_sections),
            "document_distribution": {doc: len([s for s in sources if s.get("doc_id") == doc]) for doc in unique_docs}
        }
    
    def format_error_response(self, error: str, query: str) -> Dict[str, Any]:
        """Format enhanced error responses"""
        return {
            "response_id": self._generate_response_id(),
            "timestamp": datetime.utcnow().isoformat() if self.config.include_timestamps else None,
            "answer": "I apologize, but I encountered an error while processing your query. Please try rephrasing your question or contact support if the issue persists.",
            "response_type": ResponseType.ERROR.value,
            "category": "error",
            "query": {
                "original": query,
                "processed": query,
                "language": "en",
                "intent": {"primary_intent": "error", "all_intents": [], "complexity": "unknown"}
            },
            "confidence": {
                "score": 0.0,
                "level": ConfidenceLevel.VERY_LOW.value,
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
    
    def format_no_results_response(self, query: str, threshold: float) -> Dict[str, Any]:
        """Format enhanced no-results responses"""
        return {
            "response_id": self._generate_response_id(),
            "timestamp": datetime.utcnow().isoformat() if self.config.include_timestamps else None,
            "answer": "I couldn't find specific information about this in the available policy documents. Please try rephrasing your question or check if the relevant documents have been uploaded.",
            "response_type": ResponseType.NO_RESULTS.value,
            "category": "no_results",
            "query": {
                "original": query,
                "processed": query,
                "language": "en",
                "intent": self._analyze_query_intent(query)
            },
            "confidence": {
                "score": 0.0,
                "level": ConfidenceLevel.VERY_LOW.value,
                "breakdown": {"overall": 0.0, "source_relevance": 0.0, "response_completeness": 0.0, "citation_quality": 0.0}
            },
            "sources": {
                "total_count": 0,
                "documents": [],
                "coverage": {"documents": 0, "pages": 0, "sections": 0, "total_chunks": 0}
            },
            "search_parameters": {
                "threshold_used": threshold,
                "adaptive_threshold": True,
                "retrieval_method": "semantic_search"
            },
            "quality_indicators": {
                "completeness": 0.0,
                "specificity": 0.0,
                "citation_count": 0
            },
            "warnings": [
                {
                    "type": "no_sources",
                    "severity": "high",
                    "message": "No relevant documents found",
                    "suggestion": "Upload additional policy documents"
                },
                {
                    "type": "query_rephrasing",
                    "severity": "medium",
                    "message": "Consider rephrasing your question",
                    "suggestion": "Try using different keywords"
                }
            ],
            "recommendations": [
                {
                    "type": "upload_documents",
                    "priority": "high",
                    "suggestion": "Upload additional policy documents",
                    "examples": ["Policy schedules", "Endorsements", "Riders"]
                },
                {
                    "type": "improve_query",
                    "priority": "medium",
                    "suggestion": "Try using more specific terms",
                    "examples": ["Instead of 'coverage', try 'what medical expenses are covered'"]
                }
            ]
        }

# Global formatter instance
response_formatter = EnhancedLegalResponseFormatter()