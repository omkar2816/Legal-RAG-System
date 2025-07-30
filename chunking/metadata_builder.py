"""
Metadata builder for document chunks
"""
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MetadataBuilder:
    """Builds comprehensive metadata for document chunks"""
    
    def __init__(self):
        self.legal_terms = [
            "whereas", "hereby", "hereinafter", "party", "parties", "agreement",
            "contract", "clause", "section", "article", "paragraph", "subparagraph",
            "jurisdiction", "governing law", "dispute resolution", "arbitration",
            "breach", "termination", "liability", "indemnification", "confidentiality",
            "intellectual property", "force majeure", "amendment", "waiver"
        ]
    
    def build_metadata(self, chunks: List[Dict[str, Any]], doc_id: str, 
                      doc_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Build metadata for chunks
        
        Args:
            chunks: List of chunk dictionaries
            doc_id: Document ID
            doc_metadata: Additional document metadata
        
        Returns:
            List of metadata dictionaries
        """
        metadata_list = []
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = self._build_chunk_metadata(chunk, doc_id, i, doc_metadata)
            metadata_list.append(chunk_metadata)
        
        return metadata_list
    
    def _build_chunk_metadata(self, chunk: Dict[str, Any], doc_id: str, 
                            chunk_idx: int, doc_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build metadata for a single chunk
        
        Args:
            chunk: Chunk dictionary
            doc_id: Document ID
            chunk_idx: Chunk index
            doc_metadata: Document metadata
        
        Returns:
            Metadata dictionary
        """
        # Base metadata
        metadata = {
            "doc_id": doc_id,
            "chunk_id": chunk.get('chunk_id', f"chunk_{chunk_idx}"),
            "chunk_idx": chunk_idx,
            "text": chunk.get('text', ''),
            "word_count": chunk.get('word_count', 0),
            "timestamp": datetime.utcnow().isoformat(),
            "content_hash": self._hash_content(chunk.get('text', '')),
        }
        
        # Add section information if available
        if 'section_title' in chunk:
            metadata.update({
                "section_title": chunk['section_title'],
                "section_idx": chunk['section_idx']
            })
        
        # Add position information
        if 'start_word' in chunk and 'end_word' in chunk:
            metadata.update({
                "start_word": chunk['start_word'],
                "end_word": chunk['end_word']
            })
        
        # Add document metadata
        if doc_metadata:
            metadata.update({
                "doc_type": doc_metadata.get('doc_type', 'unknown'),
                "doc_title": doc_metadata.get('title', ''),
                "doc_author": doc_metadata.get('author', ''),
                "doc_date": doc_metadata.get('date', ''),
                "doc_source": doc_metadata.get('source', ''),
                "doc_category": doc_metadata.get('category', ''),
            })
        
        # Add legal term analysis
        legal_analysis = self._analyze_legal_terms(chunk.get('text', ''))
        metadata.update(legal_analysis)
        
        return metadata
    
    def _hash_content(self, content: str) -> str:
        """
        Generate hash for content
        
        Args:
            content: Text content
        
        Returns:
            Content hash
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _analyze_legal_terms(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for legal terms
        
        Args:
            text: Text to analyze
        
        Returns:
            Legal analysis results
        """
        text_lower = text.lower()
        
        # Count legal terms
        term_counts = {}
        for term in self.legal_terms:
            count = text_lower.count(term.lower())
            if count > 0:
                term_counts[term] = count
        
        # Calculate legal term density
        total_words = len(text.split())
        legal_word_count = sum(term_counts.values())
        legal_density = legal_word_count / total_words if total_words > 0 else 0
        
        return {
            "legal_terms": term_counts,
            "legal_term_count": legal_word_count,
            "legal_density": legal_density,
            "is_legal_document": legal_density > 0.01  # 1% threshold
        }
    
    def build_document_metadata(self, file_path: str, file_type: str, 
                               content: str = None) -> Dict[str, Any]:
        """
        Build metadata for a document
        
        Args:
            file_path: Path to the document
            file_type: Type of document
            content: Document content (optional)
        
        Returns:
            Document metadata
        """
        import os
        
        metadata = {
            "doc_id": self._generate_doc_id(file_path),
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_type": file_type,
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "upload_timestamp": datetime.utcnow().isoformat(),
        }
        
        # Analyze content if provided
        if content:
            analysis = self._analyze_legal_terms(content)
            metadata.update({
                "total_words": len(content.split()),
                "legal_density": analysis["legal_density"],
                "is_legal_document": analysis["is_legal_document"]
            })
        
        return metadata
    
    def _generate_doc_id(self, file_path: str) -> str:
        """
        Generate unique document ID
        
        Args:
            file_path: File path
        
        Returns:
            Document ID
        """
        import os
        file_name = os.path.basename(file_path)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{file_name}_{timestamp}"

# Global metadata builder instance
metadata_builder = MetadataBuilder()

def build_metadata(chunks: List[Dict[str, Any]], doc_id: str, 
                  doc_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to build metadata
    
    Args:
        chunks: List of chunks
        doc_id: Document ID
        doc_metadata: Document metadata
    
    Returns:
        List of metadata dictionaries
    """
    return metadata_builder.build_metadata(chunks, doc_id, doc_metadata)