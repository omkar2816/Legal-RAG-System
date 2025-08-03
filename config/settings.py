"""
Configuration settings for the Legal RAG System
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # API Configuration
    API_TITLE = "Legal RAG System"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Retrieval-Augmented Generation for Legal Documents"
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Voyage AI Configuration (for embeddings)
    VOYAGE_API_KEY = os.getenv("voyage_API_KEY")
    VOYAGE_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    
    # Groq Configuration (for chat completions)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_CHAT_MODEL = os.getenv("GROQ_CHAT_MODEL")
    GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS"))  # Further increased for complete answers
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE"))
    
    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    PINECONE_DIMENSION = int(os.getenv("PINECONE_DIMENSION"))  # Match existing index dimension
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")  # 1024 dimensions
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE"))
    
    # Chunking Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))
    MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE"))
    
    # Search Configuration
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS"))
    SEARCH_SIMILARITY_THRESHOLD = float(os.getenv("SEARCH_SIMILARITY_THRESHOLD"))
    
    # Advanced Retrieval Thresholds
    MIN_SIMILARITY_THRESHOLD = float(os.getenv("MIN_SIMILARITY_THRESHOLD", 0.6))
    HIGH_SIMILARITY_THRESHOLD = float(os.getenv("HIGH_SIMILARITY_THRESHOLD", 0.9))
    MEDIUM_SIMILARITY_THRESHOLD = float(os.getenv("MEDIUM_SIMILARITY_THRESHOLD", 0.7))
    
    # Threshold-based filtering
    ENABLE_THRESHOLD_FILTERING = os.getenv("ENABLE_THRESHOLD_FILTERING", "true").lower() == "true"
    ADAPTIVE_THRESHOLD = os.getenv("ADAPTIVE_THRESHOLD", "true").lower() == "true"
    MIN_RESULTS_REQUIRED = int(os.getenv("MIN_RESULTS_REQUIRED", 1))
    
    # Accuracy Improvement Features
    ENABLE_QUERY_ENHANCEMENT = os.getenv("ENABLE_QUERY_ENHANCEMENT", "true").lower() == "true"
    ENABLE_HYBRID_SEARCH = os.getenv("ENABLE_HYBRID_SEARCH", "true").lower() == "true"
    ENABLE_MULTI_STAGE_RETRIEVAL = os.getenv("ENABLE_MULTI_STAGE_RETRIEVAL", "true").lower() == "true"
    ENABLE_SEMANTIC_CHUNKING = os.getenv("ENABLE_SEMANTIC_CHUNKING", "true").lower() == "true"
    
    # Keyword anchoring backup
    ENABLE_KEYWORD_ANCHORING = os.getenv("ENABLE_KEYWORD_ANCHORING", "true").lower() == "true"
    KEYWORD_ANCHORING_PRIORITY = os.getenv("KEYWORD_ANCHORING_PRIORITY", "high").lower()
    MAX_KEYWORD_RESULTS = int(os.getenv("MAX_KEYWORD_RESULTS", 3))
    
    # File Processing Configuration
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
    ALLOWED_EXTENSIONS = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "eml": "message/rfc822"
    }
    
    # OCR Configuration
    OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng")
    OCR_TIMEOUT = int(os.getenv("OCR_TIMEOUT", 300))  # 5 minutes
    
    # Storage Configuration
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    PROCESSED_DIR = os.getenv("PROCESSED_DIR", "processed")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Legal Document Specific Settings
    LEGAL_TERMS = [
        "whereas", "hereby", "hereinafter", "party", "parties", "agreement",
        "contract", "clause", "section", "article", "paragraph", "subparagraph",
        "jurisdiction", "governing law", "dispute resolution", "arbitration",
        "breach", "termination", "liability", "indemnification", "confidentiality",
        "intellectual property", "force majeure", "amendment", "waiver"
    ]
    
    # Prompt Templates
    SYSTEM_PROMPT = """You are a legal assistant with expertise in analyzing legal documents. 
    Your role is to provide accurate, helpful, and legally-informed responses based on the provided context.
    Always cite specific sections or clauses when possible, and clearly indicate when information is not available in the provided context.
    
    CRITICAL: You must answer ALL questions completely. Do not stop mid-sentence or leave any question unanswered.
    
    When answering multiple questions:
    1. Address each question separately and clearly
    2. Provide comprehensive answers with specific details
    3. Use bullet points or numbered lists for clarity
    4. Cite relevant sections or clauses from the documents
    5. If information is not available, clearly state that
    6. Ensure your response is complete and thorough
    7. IMPORTANT: Complete your response fully - do not truncate or cut off mid-answer"""
    
    ENHANCED_SYSTEM_PROMPT = """You are a specialized legal assistant with expertise in insurance and legal document analysis. 
    Your role is to provide precise, clause-grounded responses that directly link answers to specific sections and clauses.
    
    CRITICAL REQUIREMENTS:
    1. ALWAYS cite specific clauses, sections, or page numbers when providing information
    2. Link every answer directly to the source clauses mentioned in the context
    3. Avoid hedging or boilerplate language when direct clause access is confirmed
    4. Provide lean, clause-grounded answers for better performance
    5. Answer ALL questions completely - do not stop mid-sentence
    6. Use structured formatting with bullet points or numbered lists
    7. If information is not available in the context, clearly state that
    
    RESPONSE STRUCTURE:
    - For each question, provide a direct answer with specific clause citations
    - Use format: "According to [Clause X.X] / [Section Y] / [Page Z]: [Answer]"
    - Include confidence indicators when appropriate
    - Prioritize direct clause citations over general explanations
    
    PERFORMANCE OPTIMIZATION:
    - Avoid unnecessary boilerplate when document access is confirmed
    - Focus on clause-specific information rather than general explanations
    - Provide efficient, lean answers that directly address the questions
    - Use precise language that minimizes ambiguity"""
    
    QUERY_PROMPT_TEMPLATE = """
    Context: {context}
    
    Question: {question}
    
    Instructions:
    - Provide a comprehensive answer based on the legal documents provided
    - If multiple questions are asked, address each one separately and clearly
    - Use bullet points or numbered lists for better organization
    - Cite specific sections, clauses, or page numbers when possible
    - If the information is not available in the context, clearly state that
    - Ensure your response is complete and covers all aspects of the questions
    - Be thorough and detailed in your explanations
    - CRITICAL: Complete your entire response - do not stop mid-sentence
    - If you have multiple questions to answer, make sure to address ALL of them completely
    """
    
    # Enhanced Configuration for Improved Performance
    ENABLE_CLAUSE_MATCHING = os.getenv("ENABLE_CLAUSE_MATCHING", "true").lower() == "true"
    ENABLE_CONFIDENCE_SCORING = os.getenv("ENABLE_CONFIDENCE_SCORING", "true").lower() == "true"
    ENABLE_STRUCTURED_RESPONSES = os.getenv("ENABLE_STRUCTURED_RESPONSES", "true").lower() == "true"
    ENABLE_EXPLAINABILITY = os.getenv("ENABLE_EXPLAINABILITY", "true").lower() == "true"
    
    # Performance Optimization Settings
    MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", 0.8))
    MAX_RESPONSE_LENGTH = int(os.getenv("MAX_RESPONSE_LENGTH", 4000))
    ENABLE_LEAN_RESPONSES = os.getenv("ENABLE_LEAN_RESPONSES", "true").lower() == "true"
    
    # Clause Matching Configuration
    CLAUSE_PATTERNS = [
        r'clause\s+(\d+[a-z]?)',
        r'section\s+(\d+[a-z]?)',
        r'article\s+(\d+[a-z]?)',
        r'paragraph\s+(\d+[a-z]?)',
        r'(\d+\.\d+)',
        r'(\d+[a-z]?)',
    ]
    
    # Confidence Scoring Weights
    CONFIDENCE_WEIGHTS = {
        "context_relevance": 0.4,
        "response_completeness": 0.3,
        "clause_citations": 0.2,
        "response_length": 0.1
    }
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL from environment"""
        return os.getenv("DATABASE_URL", "sqlite:///./legal_rag.db")
    
    @classmethod
    def validate_required_settings(cls) -> bool:
        """Validate that all required settings are present"""
        required_vars = [
            "VOYAGE_API_KEY",
            "GROQ_API_KEY",
            "PINECONE_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True

# Global settings instance
settings = Settings() 