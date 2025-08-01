"""
Validation utilities for the Legal RAG System
"""
import re
from typing import List, Dict, Any, Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ValidationUtils:
    """Utility class for input validation"""
    
    def __init__(self):
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS.keys()
        self.max_file_size = settings.MAX_FILE_SIZE
    
    def validate_file_upload(self, filename: str, file_size: int, 
                           content_type: str = None) -> Dict[str, Any]:
        """
        Validate file upload
        
        Args:
            filename: Name of uploaded file
            file_size: Size of file in bytes
            content_type: MIME type of file
        
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check file extension
        if not self._validate_file_extension(filename):
            result["valid"] = False
            result["errors"].append(f"File extension not allowed. Allowed: {', '.join(self.allowed_extensions)}")
        
        # Check file size
        if file_size > self.max_file_size:
            result["valid"] = False
            result["errors"].append(f"File too large. Max size: {self.max_file_size / (1024*1024):.1f}MB")
        
        # Check content type if provided
        if content_type and not self._validate_content_type(content_type):
            result["warnings"].append(f"Content type '{content_type}' may not match file extension")
        
        return result
    
    def _validate_file_extension(self, filename: str) -> bool:
        """
        Validate file extension
        
        Args:
            filename: Filename to validate
        
        Returns:
            True if extension is allowed
        """
        if not filename:
            return False
        
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return ext in self.allowed_extensions
    
    def _validate_content_type(self, content_type: str) -> bool:
        """
        Validate content type
        
        Args:
            content_type: MIME type to validate
        
        Returns:
            True if content type is allowed
        """
        allowed_types = list(settings.ALLOWED_EXTENSIONS.values())
        return content_type in allowed_types
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """
        Validate search query
        
        Args:
            query: Search query string
        
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "cleaned_query": query
        }
        
        # Check if query is empty
        if not query or not query.strip():
            result["valid"] = False
            result["errors"].append("Query cannot be empty")
            return result
        
        # Clean and normalize query
        cleaned_query = query.strip()
        normalized_query = self.normalize_query(cleaned_query)
        
        # Check minimum length
        if len(normalized_query) < 3:
            result["warnings"].append("Query is very short, may not return relevant results")
        
        # Check for potentially problematic characters
        if re.search(r'[<>{}]', normalized_query):
            result["warnings"].append("Query contains special characters that may affect search")
        
        # Check for legal terms (optional enhancement)
        legal_terms = settings.LEGAL_TERMS
        found_legal_terms = [term for term in legal_terms if term.lower() in normalized_query.lower()]
        if found_legal_terms:
            result["warnings"].append(f"Query contains legal terms: {', '.join(found_legal_terms)}")
        
        # Add warning if query was normalized
        if normalized_query != cleaned_query.lower():
            result["warnings"].append("Query was normalized for better search results")
        
        result["cleaned_query"] = normalized_query
        return result
    
    def validate_document_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate document metadata
        
        Args:
            metadata: Document metadata dictionary
        
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = ["doc_id", "file_name"]
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                result["valid"] = False
                result["errors"].append(f"Missing required field: {field}")
        
        # Validate doc_id format
        if "doc_id" in metadata:
            doc_id = metadata["doc_id"]
            if not re.match(r'^[a-zA-Z0-9_-]+$', doc_id):
                result["warnings"].append("Document ID contains special characters")
        
        # Validate file size if present
        if "file_size" in metadata:
            try:
                file_size = int(metadata["file_size"])
                if file_size <= 0:
                    result["errors"].append("File size must be positive")
                elif file_size > self.max_file_size:
                    result["errors"].append(f"File size exceeds maximum allowed size")
            except (ValueError, TypeError):
                result["errors"].append("Invalid file size value")
        
        return result
    
    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text input
        
        Args:
            text: Input text
        
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>{}]', '', text)
        
        # Limit length
        max_length = 10000  # Reasonable limit for text processing
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text.strip()
    
    def normalize_query(self, query: str) -> str:
        """
        Normalize query by applying synonym replacements and standardization
        
        Args:
            query: Input query string
        
        Returns:
            Normalized query string
        """
        if not query:
            return ""
        
        # Convert to lowercase and strip whitespace
        query = query.lower().strip()
        
        # Define synonyms for legal terms
        synonyms = {
            "preexisting diseases": ["pre-existing disease", "PED", "existing illness", "pre-existing condition"],
            "expenses": ["coverage", "limit", "exclusion", "claim amount", "costs", "medical expenses"],
            "coverage": ["insurance coverage", "policy coverage", "benefits", "protection"],
            "deductible": ["deductible amount", "deductible limit", "out-of-pocket"],
            "premium": ["insurance premium", "monthly premium", "annual premium", "payment"],
            "claim": ["insurance claim", "claim filing", "claim process", "claim submission"],
            "exclusion": ["excluded conditions", "not covered", "excluded items", "limitations"],
            "waiting period": ["waiting time", "wait period", "exclusion period", "initial period"],
            "renewal": ["policy renewal", "renewal process", "renewal terms", "extension"],
            "termination": ["policy termination", "cancellation", "end of coverage", "discontinuation"]
        }
        
        # Apply synonym replacements
        for standard_term, synonym_list in synonyms.items():
            for synonym in synonym_list:
                if synonym in query:
                    query = query.replace(synonym, standard_term)
        
        return query
    
    def validate_search_parameters(self, top_k: int = None, 
                                 similarity_threshold: float = None) -> Dict[str, Any]:
        """
        Validate search parameters
        
        Args:
            top_k: Number of results to return
            similarity_threshold: Similarity threshold
        
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "cleaned_params": {}
        }
        
        # Validate top_k
        if top_k is not None:
            try:
                top_k = int(top_k)
                if top_k <= 0:
                    result["valid"] = False
                    result["errors"].append("top_k must be positive")
                elif top_k > 50:
                    result["warnings"].append("top_k is very high, may impact performance")
                else:
                    result["cleaned_params"]["top_k"] = top_k
            except (ValueError, TypeError):
                result["valid"] = False
                result["errors"].append("Invalid top_k value")
        
        # Validate similarity threshold
        if similarity_threshold is not None:
            try:
                similarity_threshold = float(similarity_threshold)
                if similarity_threshold < 0 or similarity_threshold > 1:
                    result["valid"] = False
                    result["errors"].append("similarity_threshold must be between 0 and 1")
                else:
                    result["cleaned_params"]["similarity_threshold"] = similarity_threshold
            except (ValueError, TypeError):
                result["valid"] = False
                result["errors"].append("Invalid similarity_threshold value")
        
        return result

# Global validation utils instance
validation_utils = ValidationUtils() 