"""
LLM client for generating responses using OpenAI
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with OpenAI LLM"""
    
    def __init__(self, model: str = None, temperature: float = None, max_tokens: int = None):
        self.model = model or settings.OPENAI_MODEL
        self.temperature = temperature or settings.OPENAI_TEMPERATURE
        self.max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def generate_response(self, prompt: str, context: str = None, 
                         system_prompt: str = None) -> str:
        """
        Generate response using LLM
        
        Args:
            prompt: User prompt
            context: Context information
            system_prompt: System prompt
        
        Returns:
            Generated response
        """
        messages = []
        
        # Add system message
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": settings.SYSTEM_PROMPT})
        
        # Add context if provided
        if context:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
        else:
            full_prompt = prompt
        
        messages.append({"role": "user", "content": full_prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return f"Error generating response: {str(e)}"
    
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

def call_llm(prompt: str, model: str = "gpt-3.5-turbo") -> str:
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