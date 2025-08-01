"""
Response Formatter for Legal RAG System
Standardizes query responses with proper formatting, length control, and threshold handling
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ResponseType(Enum):
    """Types of legal responses"""
    DIRECT_ANSWER = "direct_answer"
    PROCEDURAL = "procedural"
    EXCLUSION = "exclusion"
    COVERAGE = "coverage"
    CLAIM = "claim"
    GENERAL = "general"

@dataclass
class ResponseConfig:
    """Configuration for response formatting"""
    max_length: int = 300
    min_length: int = 50
    include_sources: bool = True
    include_confidence: bool = True
    include_threshold_info: bool = True
    format_type: str = "structured"

class LegalResponseFormatter:
    """
    Formats legal responses with consistent structure, length, and threshold handling
    """
    
    def __init__(self, config: Optional[ResponseConfig] = None):
        self.config = config or ResponseConfig()
        self.response_templates = {
            ResponseType.DIRECT_ANSWER: {
                "template": "Based on the policy document, {answer}",
                "max_length": 250
            },
            ResponseType.PROCEDURAL: {
                "template": "According to the policy procedures: {answer}",
                "max_length": 300
            },
            ResponseType.EXCLUSION: {
                "template": "Important: {answer}",
                "max_length": 280
            },
            ResponseType.COVERAGE: {
                "template": "Coverage information: {answer}",
                "max_length": 300
            },
            ResponseType.CLAIM: {
                "template": "Claim process details: {answer}",
                "max_length": 350
            },
            ResponseType.GENERAL: {
                "template": "{answer}",
                "max_length": 300
            }
        }
    
    def format_response(
        self,
        answer: str,
        sources: List[Dict[str, Any]],
        confidence: float,
        query: str,
        threshold_used: float
    ) -> Dict[str, Any]:
        """
        Format a complete response with proper structure and threshold handling
        
        Args:
            answer: Raw answer from LLM
            sources: List of source documents
            confidence: Confidence score
            query: Original query
            threshold_used: Threshold used for filtering
            
        Returns:
            Formatted response dictionary
        """
        # Determine response type
        response_type = self._classify_response_type(query, answer)
        
        # Clean and format the answer
        formatted_answer = self._format_answer(answer, response_type)
        
        # Apply length constraints
        formatted_answer = self._apply_length_constraints(formatted_answer, response_type)
        
        # Format sources with threshold information
        formatted_sources = self._format_sources(sources, threshold_used)
        
        # Create response structure
        response = {
            "answer": formatted_answer,
            "response_type": response_type.value,
            "confidence": self._format_confidence(confidence),
            "total_sources": len(formatted_sources),
            "threshold_used": threshold_used,
            "query_processed": query
        }
        
        if self.config.include_sources:
            response["sources"] = formatted_sources
        
        # Add warnings if confidence is low
        warnings = self._generate_warnings(confidence, threshold_used, len(sources))
        if warnings:
            response["warnings"] = warnings
        
        return response
    
    def _classify_response_type(self, query: str, answer: str) -> ResponseType:
        """Classify the type of response based on query and answer content"""
        query_lower = query.lower()
        answer_lower = answer.lower()
        
        # Check for waiting period queries
        if any(term in query_lower for term in ["waiting period", "wait period", "waiting time"]):
            return ResponseType.DIRECT_ANSWER
        
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
        
        if len(text) <= max_length:
            return text
        
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
    
    def _format_sources(self, sources: List[Dict[str, Any]], threshold_used: float) -> List[Dict[str, Any]]:
        """Format sources with threshold information"""
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
                "text_preview": self._truncate_text(source.get("text", ""), 150)
            }
            
            # Add keyword information if available
            if source.get("keyword_matches"):
                formatted_source["keyword_matches"] = source.get("keyword_matches")
            
            formatted_sources.append(formatted_source)
        
        return formatted_sources
    
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
    
    def _generate_warnings(self, confidence: float, threshold: float, source_count: int) -> List[str]:
        """Generate warnings based on response quality"""
        warnings = []
        
        if confidence < 0.5:
            warnings.append("Low confidence response - consider rephrasing your question")
        
        if threshold < 0.3:
            warnings.append("Using low similarity threshold - results may be less relevant")
        
        if source_count == 0:
            warnings.append("No relevant documents found - answer may be incomplete")
        elif source_count == 1:
            warnings.append("Limited source material - consider checking additional documents")
        
        return warnings
    
    def format_error_response(self, error: str, query: str) -> Dict[str, Any]:
        """Format error responses consistently"""
        return {
            "answer": "I apologize, but I encountered an error while processing your query. Please try rephrasing your question or contact support if the issue persists.",
            "response_type": "error",
            "confidence": 0.0,
            "total_sources": 0,
            "threshold_used": 0.0,
            "query_processed": query,
            "error": error,
            "warnings": ["Technical error occurred during processing"]
        }
    
    def format_no_results_response(self, query: str, threshold: float) -> Dict[str, Any]:
        """Format responses when no results are found"""
        return {
            "answer": "I couldn't find specific information about this in the available policy documents. Please try rephrasing your question or check if the relevant documents have been uploaded.",
            "response_type": "no_results",
            "confidence": 0.0,
            "total_sources": 0,
            "threshold_used": threshold,
            "query_processed": query,
            "sources": [],
            "warnings": [
                "No relevant documents found",
                "Consider uploading additional policy documents",
                "Try using different keywords in your question"
            ]
        }

# Global formatter instance
response_formatter = LegalResponseFormatter()