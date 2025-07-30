"""
Legal document chunking utilities
"""
import re
from typing import List, Dict, Any
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class LegalDocumentChunker:
    """Advanced chunking for legal documents with semantic awareness"""
    
    def __init__(self, chunk_size: int = None, overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.overlap = overlap or settings.CHUNK_OVERLAP
        self.legal_terms = settings.LEGAL_TERMS
        
        # Legal document patterns
        self.section_patterns = [
            r'^ARTICLE\s+\d+[\.:]?\s*[A-Z\s]+',
            r'^SECTION\s+\d+[\.:]?\s*[A-Z\s]+',
            r'^CLAUSE\s+\d+[\.:]?\s*[A-Z\s]+',
            r'^PARAGRAPH\s+\d+[\.:]?\s*[A-Z\s]+',
            r'^\d+\.\s*[A-Z\s]+',
            r'^[A-Z][A-Z\s]{3,}:',
        ]
        
        # Compile patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.section_patterns]
    
    def split_by_sections(self, text: str) -> List[str]:
        """
        Split text by legal document sections
        
        Args:
            text: Input text
        
        Returns:
            List of section chunks
        """
        lines = text.split('\n')
        sections = []
        current_section = []
        
        for line in lines:
            # Check if line starts a new section
            is_section_start = any(pattern.match(line.strip()) for pattern in self.compiled_patterns)
            
            if is_section_start and current_section:
                # Save current section and start new one
                sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        # Add the last section
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def chunk_text(self, text: str, preserve_sections: bool = True) -> List[Dict[str, Any]]:
        """
        Chunk text with metadata
        
        Args:
            text: Input text
            preserve_sections: Whether to preserve legal sections
        
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        if preserve_sections:
            # Split by sections first
            sections = self.split_by_sections(text)
            
            for section_idx, section in enumerate(sections):
                section_chunks = self._chunk_section(section, section_idx)
                chunks.extend(section_chunks)
        else:
            # Simple sliding window chunking
            chunks = self._sliding_window_chunk(text)
        
        return chunks
    
    def _chunk_section(self, section: str, section_idx: int) -> List[Dict[str, Any]]:
        """
        Chunk a single section
        
        Args:
            section: Section text
            section_idx: Section index
        
        Returns:
            List of chunks with metadata
        """
        # Extract section title
        lines = section.split('\n')
        section_title = ""
        content_start = 0
        
        for i, line in enumerate(lines):
            if any(pattern.match(line.strip()) for pattern in self.compiled_patterns):
                section_title = line.strip()
                content_start = i + 1
                break
        
        # Get section content
        section_content = '\n'.join(lines[content_start:])
        
        # Chunk the content
        content_chunks = self._sliding_window_chunk(section_content)
        
        # Add section metadata
        for i, chunk in enumerate(content_chunks):
            chunk['section_title'] = section_title
            chunk['section_idx'] = section_idx
            chunk['chunk_id'] = f"section_{section_idx}_chunk_{i}"
        
        return content_chunks
    
    def _sliding_window_chunk(self, text: str) -> List[Dict[str, Any]]:
        """
        Sliding window chunking with overlap
        
        Args:
            text: Input text
        
        Returns:
            List of chunks with metadata
        """
        words = text.split()
        chunks = []
        
        if len(words) <= self.chunk_size:
            # Text fits in one chunk
            chunk_text = ' '.join(words)
            chunks.append({
                'text': chunk_text,
                'chunk_id': f"chunk_0",
                'word_count': len(words),
                'start_word': 0,
                'end_word': len(words)
            })
        else:
            # Multiple chunks needed
            step = self.chunk_size - self.overlap
            
            for i in range(0, len(words), step):
                end_idx = min(i + self.chunk_size, len(words))
                chunk_words = words[i:end_idx]
                chunk_text = ' '.join(chunk_words)
                
                chunks.append({
                    'text': chunk_text,
                    'chunk_id': f"chunk_{i//step}",
                    'word_count': len(chunk_words),
                    'start_word': i,
                    'end_word': end_idx
                })
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        """
        Clean text for better chunking
        
        Args:
            text: Input text
        
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up legal formatting
        text = re.sub(r'([A-Z])\s+([A-Z])', r'\1\2', text)  # Fix spacing in legal terms
        
        return text.strip()

def sliding_window(text: str, window_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Simple sliding window chunking (legacy function)
    
    Args:
        text: Input text
        window_size: Size of each chunk
        overlap: Overlap between chunks
    
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    step = window_size - overlap
    
    for i in range(0, len(words), step):
        chunk = ' '.join(words[i:i + window_size])
        chunks.append(chunk)
    
    return chunks

# Global chunker instance
legal_chunker = LegalDocumentChunker()