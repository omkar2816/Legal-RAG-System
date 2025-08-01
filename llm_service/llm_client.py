"""
LLM client for generating responses using Groq
"""
from groq import Groq
from typing import List, Dict, Any, Optional
from config.settings import settings
from utils.query_enhancer import detect_multiple_questions
import logging
import re

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with Groq LLM for chat completions.
    
    Note: Voyage AI is still used for embeddings, but Groq is used for chat completions.
    """
    def __init__(self, model: str = None, temperature: float = None, max_tokens: int = None):
        self.model = model or settings.GROQ_CHAT_MODEL
        self.temperature = temperature or settings.GROQ_TEMPERATURE
        self.max_tokens = max_tokens or settings.GROQ_MAX_TOKENS
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def generate_response(self, prompt: str, context: str = None, system_prompt: str = None) -> str:
        """
        Generate response using Groq LLM
        
        Args:
            prompt: User prompt
            context: Additional context (optional)
            system_prompt: System prompt (optional)
        
        Returns:
            Generated response
        """
        try:
            # Prepare messages
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add context if provided
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            else:
                full_prompt = prompt
            
            messages.append({"role": "user", "content": full_prompt})
            
            # Generate completion
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response with Groq: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def generate_legal_response(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate legal response with context and enhanced metadata
        
        Args:
            question: Legal question
            context_chunks: Retrieved context chunks
        
        Returns:
            Structured response with confidence, citations, and metadata
        """
        try:
            # Format context from chunks with enhanced metadata
            context_data = self._format_context_with_metadata(context_chunks)
            
            # Check if this is a multiple questions query
            logger.debug(f"Original question: {repr(question)}")
            logger.debug(f"Question type: {type(question)}")
            
            try:
                questions = detect_multiple_questions(question)
                logger.debug(f"detect_multiple_questions result: {type(questions)} - {questions}")
            except Exception as e:
                logger.error(f"Error calling detect_multiple_questions: {e}")
                logger.error(f"Falling back to original question")
                questions = [question]
            
            # Debug logging
            logger.debug(f"Questions type: {type(questions)}")
            logger.debug(f"Questions length: {len(questions) if hasattr(questions, '__len__') else 'N/A'}")
            
            # Ensure questions is a list and all items are strings
            if not isinstance(questions, list):
                logger.error(f"detect_multiple_questions returned {type(questions)} instead of list: {questions}")
                questions = [question]  # Fallback to original question
            else:
                # Validate all items in the list are strings
                validated_questions = []
                for i, q in enumerate(questions):
                    if isinstance(q, str):
                        validated_questions.append(q)
                    else:
                        logger.warning(f"Non-string question at index {i}: {type(q)} - {q}")
                        validated_questions.append(str(q))
                questions = validated_questions
            
            # Ensure we have at least one question
            if not questions:
                logger.warning("No questions detected, using original question")
                questions = [question]
            
            logger.debug(f"Final questions list: {questions}")
            
            if len(questions) > 1:
                # Multiple questions detected - use enhanced prompt
                enhanced_question = self._enhance_multiple_questions_prompt(questions)
            else:
                # Single question - use standard prompt
                enhanced_question = question
            
            # Use enhanced legal-specific prompt template
            prompt = self._create_enhanced_prompt(
                context_data["formatted_text"],
                enhanced_question,
                context_data["clause_info"]
            )
            
            # Use system prompt for better guidance
            response = self.generate_response(
                prompt=prompt,
                system_prompt=settings.ENHANCED_SYSTEM_PROMPT
            )
            
            # Validate response completeness
            response = self._validate_response_completeness(response, questions)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(
                questions, context_chunks, response
            )
            
            # Extract clause references
            clause_references = self._extract_clause_references(response, context_data["clause_info"])
            
            # Create structured response
            structured_response = {
                "answer": response,
                "questions": questions,
                "confidence_scores": confidence_scores,
                "overall_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
                "clause_references": clause_references,
                "source_clause_ref": context_data["clause_info"],
                "context_chunks_used": len(context_chunks),
                "response_type": "structured_legal",
                "metadata": {
                    "total_questions": len(questions),
                    "has_multiple_questions": len(questions) > 1,
                    "clauses_cited": len(clause_references),
                    "context_relevance": context_data["relevance_score"]
                }
            }
            
            return structured_response
            
        except Exception as e:
            logger.error(f"Error in generate_legal_response: {str(e)}")
            logger.error(f"Question: {question}")
            logger.error(f"Context chunks count: {len(context_chunks)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to generate legal response: {str(e)}")
    
    def _enhance_multiple_questions_prompt(self, questions: List[str]) -> str:
        """
        Enhance prompt for multiple questions
        
        Args:
            questions: List of individual questions
            
        Returns:
            Enhanced prompt
        """
        enhanced_parts = []
        enhanced_parts.append("Please provide comprehensive answers to ALL of the following questions:")
        enhanced_parts.append("")
        
        for i, question in enumerate(questions, 1):
            enhanced_parts.append(f"{i}. {question}")
        
        enhanced_parts.append("")
        enhanced_parts.append("IMPORTANT: Answer each question completely and thoroughly. Do not stop mid-sentence.")
        enhanced_parts.append("Use bullet points or numbered lists for clarity.")
        enhanced_parts.append("Cite specific sections or clauses when possible.")
        
        return "\n".join(enhanced_parts)
    
    def _validate_response_completeness(self, response: str, questions: List[str]) -> str:
        """
        Validate that the response is complete
        
        Args:
            response: Generated response
            questions: Original questions
            
        Returns:
            Validated/improved response
        """
        if len(questions) <= 1:
            return response
        
        # Check if response seems incomplete
        response_lower = response.lower()
        
        # Check for common incomplete patterns
        incomplete_patterns = [
            "question 1:",
            "1.",
            "first,",
            "based on",
            "according to"
        ]
        
        # Count how many questions were actually answered
        answered_count = 0
        for i in range(1, len(questions) + 1):
            # Check if this question number appears in the response
            question_markers = [f"{i}.", f"question {i}", f"q{i}", f"#{i}"]
            question_found = False
            for marker in question_markers:
                if marker in response_lower:
                    question_found = True
                    break
            if question_found:
                answered_count += 1
        
        # If not all questions were answered, add a note
        if answered_count < len(questions):
            response += f"\n\nNOTE: This response appears to be incomplete. Only {answered_count} out of {len(questions)} questions were addressed. Please ensure all questions are answered completely."
        
        return response
    
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
    
    def _format_context_with_metadata(self, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format context chunks with enhanced metadata and clause information
        
        Args:
            context_chunks: List of context chunks
        
        Returns:
            Dictionary with formatted text and metadata
        """
        formatted_contexts = []
        clause_info = []
        total_relevance = 0.0
        
        for i, chunk in enumerate(context_chunks):
            # Get metadata
            metadata = chunk.get('metadata', {})
            section_title = metadata.get('section_title', '')
            doc_title = metadata.get('doc_title', '')
            chunk_id = metadata.get('chunk_id', f'chunk_{i}')
            page_number = metadata.get('page_number', -1)
            similarity_score = chunk.get('score', 0.0)
            
            # Format chunk with clause identification
            chunk_text = chunk.get('text', '')
            
            # Identify potential clauses
            clause_identifiers = self._identify_clause_identifiers(chunk_text)
            
            # Add source information
            source_info = []
            if doc_title:
                source_info.append(f"Document: {doc_title}")
            if section_title:
                source_info.append(f"Section: {section_title}")
            if page_number > 0:
                source_info.append(f"Page: {page_number}")
            
            source_prefix = f"[{' | '.join(source_info)}] " if source_info else ""
            
            # Add clause information if found
            if clause_identifiers:
                clause_text = f" [Clauses: {', '.join(clause_identifiers)}]"
                formatted_text = f"{source_prefix}{chunk_text}{clause_text}"
            else:
                formatted_text = f"{source_prefix}{chunk_text}"
            
            formatted_contexts.append(formatted_text)
            
            # Store clause information
            clause_info.append({
                "chunk_id": chunk_id,
                "doc_title": doc_title,
                "section_title": section_title,
                "page_number": page_number,
                "similarity_score": similarity_score,
                "clause_identifiers": clause_identifiers,
                "text_preview": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text
            })
            
            total_relevance += similarity_score
        
        return {
            "formatted_text": "\n\n".join(formatted_contexts),
            "clause_info": clause_info,
            "relevance_score": total_relevance / len(context_chunks) if context_chunks else 0.0
        }
    
    def _identify_clause_identifiers(self, text: str) -> List[str]:
        """Identify potential clause identifiers in text"""
        clause_patterns = [
            r'clause\s+(\d+[a-z]?)',
            r'section\s+(\d+[a-z]?)',
            r'article\s+(\d+[a-z]?)',
            r'paragraph\s+(\d+[a-z]?)',
            r'(\d+\.\d+)',  # Section numbers like 1.1, 2.3
            r'(\d+[a-z]?)',  # Simple numbers that might be clause references
        ]
        
        identifiers = []
        for pattern in clause_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            identifiers.extend(matches)
        
        return list(set(identifiers))  # Remove duplicates
    
    def _create_enhanced_prompt(self, context_text: str, question: str, clause_info: List[Dict[str, Any]]) -> str:
        """Create enhanced prompt with clause information"""
        
        # Build clause reference section
        clause_references = []
        for clause in clause_info:
            if clause["clause_identifiers"]:
                ref = f"- {clause['section_title']} (Page {clause['page_number']}): {', '.join(clause['clause_identifiers'])}"
                clause_references.append(ref)
        
        clause_section = ""
        if clause_references:
            clause_section = f"\n\nAvailable Clauses and Sections:\n" + "\n".join(clause_references)
        
        prompt = f"""
Context: {context_text}{clause_section}

Question: {question}

Instructions:
- Provide a comprehensive answer based on the legal documents provided
- If multiple questions are asked, address each one separately and clearly
- Use bullet points or numbered lists for better organization
- ALWAYS cite specific sections, clauses, or page numbers when possible
- If the information is not available in the context, clearly state that
- Ensure your response is complete and covers all aspects of the questions
- Be thorough and detailed in your explanations
- CRITICAL: Complete your entire response - do not stop mid-sentence
- If you have multiple questions to answer, make sure to address ALL of them completely
- IMPORTANT: Link your answers directly to specific clauses and sections mentioned in the context
"""
        
        return prompt
    
    def _calculate_confidence_scores(self, questions: List[str], context_chunks: List[Dict[str, Any]], response: str) -> List[float]:
        """Calculate confidence scores for each question"""
        confidence_scores = []
        
        for question in questions:
            # Calculate confidence based on multiple factors
            factors = []
            
            # 1. Context relevance
            avg_similarity = sum(chunk.get('score', 0) for chunk in context_chunks) / len(context_chunks) if context_chunks else 0
            factors.append(min(avg_similarity, 1.0))
            
            # 2. Response completeness
            question_lower = question.lower()
            response_lower = response.lower()
            
            # Check if question keywords appear in response
            question_words = set(re.findall(r'\w+', question_lower))
            response_words = set(re.findall(r'\w+', response_lower))
            word_overlap = len(question_words.intersection(response_words)) / len(question_words) if question_words else 0
            factors.append(word_overlap)
            
            # 3. Clause citation presence
            clause_patterns = [r'clause\s+\d+', r'section\s+\d+', r'article\s+\d+', r'page\s+\d+']
            has_citations = any(re.search(pattern, response_lower) for pattern in clause_patterns)
            factors.append(0.8 if has_citations else 0.3)
            
            # 4. Response length adequacy
            response_length = len(response)
            length_score = min(response_length / 500, 1.0)  # Normalize to 500 chars
            factors.append(length_score)
            
            # Calculate weighted average
            weights = [0.4, 0.3, 0.2, 0.1]  # Context, completeness, citations, length
            confidence = sum(f * w for f, w in zip(factors, weights))
            confidence_scores.append(min(confidence, 1.0))
        
        return confidence_scores
    
    def _extract_clause_references(self, response: str, clause_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract clause references from response"""
        references = []
        
        # Extract clause mentions from response
        clause_patterns = [
            (r'clause\s+(\d+[a-z]?)', 'clause'),
            (r'section\s+(\d+[a-z]?)', 'section'),
            (r'article\s+(\d+[a-z]?)', 'article'),
            (r'page\s+(\d+)', 'page'),
            (r'(\d+\.\d+)', 'subsection'),
        ]
        
        for pattern, ref_type in clause_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                # Find corresponding clause info
                matching_clause = None
                for clause in clause_info:
                    if match in clause.get('clause_identifiers', []):
                        matching_clause = clause
                        break
                
                references.append({
                    "type": ref_type,
                    "identifier": match,
                    "context": matching_clause,
                    "found_in_response": True
                })
        
        return references
    
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

def call_llm(prompt: str, model: str = "llama3-8b-8192") -> str:
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