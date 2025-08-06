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
        
        # Simplify document metadata to reduce size
        simplified_doc_metadata = None
        if doc_metadata:
            simplified_doc_metadata = {
                'doc_type': doc_metadata.get('doc_type', 'unknown'),
                'doc_title': doc_metadata.get('title', ''),
                'doc_id': doc_id
            }
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = self._build_chunk_metadata(chunk, doc_id, i, simplified_doc_metadata)
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
        # Base metadata - REDUCED to prevent exceeding Pinecone's 40KB limit
        metadata = {
            "doc_id": doc_id,
            "chunk_id": chunk.get('chunk_id', f"chunk_{chunk_idx}"),
            "chunk_idx": chunk_idx,
            # Remove full text from metadata to reduce size
            # "text": chunk.get('text', ''),
            "word_count": chunk.get('word_count', 0),
            # Store only the first 10 characters of the timestamp to save space
            "timestamp": datetime.utcnow().isoformat()[:10],
            # Remove content_hash to save space
            # "content_hash": self._hash_content(chunk.get('text', '')),
        }
        
        # Add section information if available, but limit title length
        if 'section_title' in chunk:
            # Truncate section title to 50 characters to save space
            section_title = chunk['section_title'][:50] if len(chunk['section_title']) > 50 else chunk['section_title']
            metadata.update({
                "section_title": section_title,
                "section_idx": chunk['section_idx']
            })
        
        # Remove position information to save space
        # if 'start_word' in chunk and 'end_word' in chunk:
        #     metadata.update({
        #         "start_word": chunk['start_word'],
        #         "end_word": chunk['end_word']
        #     })
        
        # Add document metadata if provided - but only essential fields
        if doc_metadata:
            # Add only the most important document metadata
            metadata.update({
                "doc_type": doc_metadata.get('doc_type', 'unknown'),
                "doc_title": doc_metadata.get('title', '')[:100] if doc_metadata.get('title', '') and len(doc_metadata.get('title', '')) > 100 else doc_metadata.get('title', ''),
                # Remove less important fields to save space
                # "doc_author": doc_metadata.get('author', 'Unknown'),
                # "doc_date": doc_metadata.get('date', ''),
                # "doc_source": doc_metadata.get('source', ''),
                # "doc_category": doc_metadata.get('category', ''),
            })
        else:
            # Ensure only essential fields have default values
            metadata.update({
                "doc_type": "unknown",
                "doc_title": "",
                # Remove less important fields to save space
                # "doc_author": "Unknown",
                # "doc_date": "",
                # "doc_source": "",
                # "doc_category": "",
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
        
        # Further reduce metadata size by only storing top 3 most frequent terms
        # and truncating term length if necessary
        top_terms = sorted(term_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_terms_list = [term[:30] for term, _ in top_terms]  # Limit each term to 30 chars
        
        return {
            # Only include legal terms if there are any to save space
            "legal_terms": top_terms_list if top_terms_list else [],  # Only store top 3 terms
            # "legal_term_count": legal_word_count,  # Remove to save space
            "legal_density": round(legal_density, 3),  # Round to 3 decimal places to save space
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
        
        # Reduce document metadata to essential fields only
        metadata = {
            "doc_id": self._generate_doc_id(file_path),
            # Store only filename, not full path to save space
            # "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_type": file_type,
            # Store file size in KB instead of bytes to save space
            "file_size_kb": round(os.path.getsize(file_path) / 1024) if os.path.exists(file_path) else 0,
            # Store only the date part of the timestamp
            "upload_date": datetime.utcnow().isoformat()[:10],
        }
        
        # Analyze content if provided - but store minimal information
        if content:
            analysis = self._analyze_legal_terms(content)
            metadata.update({
                # Round word count to nearest 100 to save space
                "total_words": round(len(content.split()) / 100) * 100,
                "legal_density": round(analysis["legal_density"], 3),
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