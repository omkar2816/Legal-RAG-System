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
    
    # Voyage AI Configuration
    VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
    VOYAGE_EMBEDDING_MODEL = os.getenv("VOYAGE_EMBEDDING_MODEL", "voyage-large-2")
    VOYAGE_CHAT_MODEL = os.getenv("VOYAGE_CHAT_MODEL", "voyage-large-2")
    VOYAGE_MAX_TOKENS = int(os.getenv("VOYAGE_MAX_TOKENS", 1000))
    VOYAGE_TEMPERATURE = float(os.getenv("VOYAGE_TEMPERATURE", 0.1))
    
    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "hackrx")
    PINECONE_DIMENSION = int(os.getenv("PINECONE_DIMENSION", 1024))  # Match existing index dimension
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "voyage-large-2")  # 1024 dimensions
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", 100))
    
    # Chunking Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE", 1500))
    
    # Search Configuration
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))
    SEARCH_SIMILARITY_THRESHOLD = float(os.getenv("SEARCH_SIMILARITY_THRESHOLD", 0.7))
    
    # Advanced Retrieval Thresholds
    MIN_SIMILARITY_THRESHOLD = float(os.getenv("MIN_SIMILARITY_THRESHOLD", 0.2))
    HIGH_SIMILARITY_THRESHOLD = float(os.getenv("HIGH_SIMILARITY_THRESHOLD", 0.8))
    MEDIUM_SIMILARITY_THRESHOLD = float(os.getenv("MEDIUM_SIMILARITY_THRESHOLD", 0.5))
    
    # Threshold-based filtering
    ENABLE_THRESHOLD_FILTERING = os.getenv("ENABLE_THRESHOLD_FILTERING", "true").lower() == "true"
    ADAPTIVE_THRESHOLD = os.getenv("ADAPTIVE_THRESHOLD", "true").lower() == "true"
    MIN_RESULTS_REQUIRED = int(os.getenv("MIN_RESULTS_REQUIRED", 1))
    
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
        "jpeg": "image/jpeg"
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
    Always cite specific sections or clauses when possible, and clearly indicate when information is not available in the provided context."""
    
    QUERY_PROMPT_TEMPLATE = """
    Context: {context}
    
    Question: {question}
    
    Please provide a comprehensive answer based on the legal documents provided. 
    If the information is not available in the context, please state that clearly.
    """
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL from environment"""
        return os.getenv("DATABASE_URL", "sqlite:///./legal_rag.db")
    
    @classmethod
    def validate_required_settings(cls) -> bool:
        """Validate that all required settings are present"""
        required_vars = [
            "VOYAGE_API_KEY",
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