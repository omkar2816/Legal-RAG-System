"""
LLM client for generating responses using Voyage AI
"""
from voyageai import Client
from typing import List, Dict, Any, Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with Voyage AI LLM (embeddings only as of 2024).
    
    Note: The Voyage AI Python client does NOT support chat/completions as of now.
    For LLM completions, use the HTTP API directly if available, or use another provider.
    """
    def __init__(self, model: str = None, temperature: float = None, max_tokens: int = None):
        self.model = model or settings.VOYAGE_CHAT_MODEL
        self.temperature = temperature or settings.VOYAGE_TEMPERATURE
        self.max_tokens = max_tokens or settings.VOYAGE_MAX_TOKENS
        self.client = Client(api_key=settings.VOYAGE_API_KEY)

    def generate_response(self, prompt: str, context: str = None, system_prompt: str = None) -> str:
        """
        Generate response using LLM (NOT IMPLEMENTED for Voyage AI Python client)
        """
        raise NotImplementedError(
            "Voyage AI Python client does not support chat/completions. "
            "Use the HTTP API directly if available, or use another provider."
        )
        # Example template for HTTP API usage (uncomment and fill in if HTTP API is available):
        # import requests
        # url = "https://api.voyageai.com/v1/chat/completions"
        # headers = {"Authorization": f"Bearer {settings.VOYAGE_API_KEY}", "Content-Type": "application/json"}
        # data = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": self.max_tokens, "temperature": self.temperature}
        # response = requests.post(url, headers=headers, json=data)
        # return response.json()["choices"][0]["message"]["content"]
    
    def generate_legal_response(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate legal response with context
        
        Args:
            question: Legal question
            context_chunks: Retrieved context chunks
        
        Returns:
            Legal response
        """
        # Format context from chunks
        context_text = self._format_context(context_chunks)
        
        # Use legal-specific prompt template
        prompt = settings.QUERY_PROMPT_TEMPLATE.format(
            context=context_text,
            question=question
        )
        
        return self.generate_response(prompt)
    
    def _format_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Format context chunks into readable text
        
        Args:
            context_chunks: List of context chunks
        
        Returns:
            Formatted context text
        """
        formatted_contexts = []
        
        for i, chunk in enumerate(context_chunks):
            # Get metadata
            metadata = chunk.get('metadata', {})
            section_title = metadata.get('section_title', '')
            doc_title = metadata.get('doc_title', '')
            
            # Format chunk
            chunk_text = chunk.get('text', '')
            
            # Add source information
            source_info = []
            if doc_title:
                source_info.append(f"Document: {doc_title}")
            if section_title:
                source_info.append(f"Section: {section_title}")
            
            source_prefix = f"[{' | '.join(source_info)}] " if source_info else ""
            
            formatted_contexts.append(f"{source_prefix}{chunk_text}")
        
        return "\n\n".join(formatted_contexts)
    
    def analyze_legal_document(self, document_text: str) -> Dict[str, Any]:
        """
        Analyze legal document structure
        
        Args:
            document_text: Document text
        
        Returns:
            Analysis results
        """
        analysis_prompt = f"""
        Analyze the following legal document and provide:
        1. Document type (contract, brief, regulation, etc.)
        2. Key parties involved
        3. Main legal issues
        4. Important clauses or sections
        5. Key dates and deadlines
        
        Document:
        {document_text[:2000]}  # Limit to first 2000 chars for analysis
        
        Provide your analysis in JSON format.
        """
        
        try:
            response = self.generate_response(analysis_prompt)
            # Note: In a production system, you'd want to parse JSON response
            return {"analysis": response, "status": "success"}
        except Exception as e:
            return {"analysis": "", "status": "error", "error": str(e)}

# Global LLM client instance
llm_client = LLMClient()

def call_llm(prompt: str, model: str = "voyage-large-2") -> str:
    """
    Convenience function for LLM calls (legacy support)
    
    Args:
        prompt: Input prompt
        model: Model name
    
    Returns:
        Generated response
    """
    client = LLMClient(model=model)
    return client.generate_response(prompt)