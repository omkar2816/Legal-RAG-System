"""
Advanced retrieval module for Legal RAG System
Combines semantic similarity with structural ranking for better document retrieval
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from utils.validation import validation_utils
from embeddings.embed_client import embedding_client
from vectordb.pinecone_client import query_embeddings
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class AdvancedRetrievalEngine:
    """
    Advanced retrieval engine that combines semantic similarity with structural ranking
    """
    
    def __init__(self):
        self.legal_keywords = {
            "preexisting_diseases": [
                "pre-existing disease", "ped", "excl 01", "preexisting condition",
                "existing illness", "pre-existing illness", "medical history"
            ],
            "exclusions": [
                "exclusion", "excluded", "not covered", "limitations",
                "excluded conditions", "coverage limitations"
            ],
            "coverage": [
                "coverage", "covered", "benefits", "insurance coverage",
                "policy coverage", "medical coverage"
            ],
            "claims": [
                "claim", "claim filing", "claim process", "claim submission",
                "claim amount", "claim limits"
            ],
            "deductibles": [
                "deductible", "deductible amount", "out-of-pocket",
                "deductible limit", "cost sharing"
            ],
            "premiums": [
                "premium", "insurance premium", "monthly premium",
                "annual premium", "payment"
            ],
            "waiting_periods": [
                "waiting period", "waiting time", "wait period",
                "exclusion period", "initial period"
            ],
            "renewals": [
                "renewal", "policy renewal", "renewal process",
                "renewal terms", "extension"
            ],
            "terminations": [
                "termination", "policy termination", "cancellation",
                "end of coverage", "discontinuation"
            ]
        }
    
    def normalize_query(self, query: str) -> str:
        """
        Normalize query using the existing validation utility
        """
        return validation_utils.normalize_query(query)
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for the query
        """
        return embedding_client.get_single_embedding(query)
    
    def calculate_structural_rank(self, text: str, query: str) -> int:
        """
        Calculate structural rank based on content relevance and legal keywords
        
        Args:
            text: Document chunk text
            query: Original query
            
        Returns:
            Rank (1 = highest priority, 3 = lowest priority)
        """
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Check for exact keyword matches in the text
        for category, keywords in self.legal_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                # Check if query is related to this category
                if any(keyword in query_lower for keyword in keywords):
                    return 1  # Highest priority - exact category match
        
        # Check for general legal terms
        if any(term in text_lower for term in ['exclusion', 'limitation', 'not covered']):
            if any(term in query_lower for term in ['exclusion', 'limit', 'not covered']):
                return 2  # Medium priority - general legal term match
        
        # Check for section headers or important structural elements
        if any(header in text_lower for header in ['section', 'article', 'clause', 'subsection']):
            return 2  # Medium priority - structural element
        
        return 3  # Lowest priority - no special relevance
    
    def retrieve_documents(
        self, 
        query: str, 
        top_k: int = 10, 
        threshold: float = 0.25,
        filter_dict: Optional[Dict[str, Any]] = None,
        return_count: int = 3,
        adaptive_threshold: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Advanced document retrieval combining semantic similarity with structural ranking
        
        Args:
            query: Search query
            top_k: Number of initial semantic results to consider
            threshold: Similarity threshold for filtering
            filter_dict: Optional filter criteria
            return_count: Number of final results to return
            adaptive_threshold: Whether to use adaptive threshold adjustment
            
        Returns:
            List of ranked document results
        """
        try:
            # Step 1: Normalize query
            normalized_query = self.normalize_query(query)
            logger.info(f"Original query: '{query}' -> Normalized: '{normalized_query}'")
            
            # Step 2: Generate query embedding
            query_vector = self.embed_query(normalized_query)
            if not query_vector:
                logger.error("Failed to generate query embedding")
                return []
            
            # Step 3: Get initial semantic results from Pinecone
            search_results = query_embeddings(
                query_vector=query_vector,
                top_k=top_k,
                filter_dict=filter_dict
            )
            
            if not search_results or 'matches' not in search_results:
                logger.warning("No search results returned from Pinecone")
                return []
            
            # Step 4: Process and rank results with enhanced threshold handling
            results = []
            all_scores = []
            
            for match in search_results['matches']:
                score = match.get('score', 0)
                all_scores.append(score)
                
                # Enhanced threshold filtering
                effective_threshold = self._calculate_effective_threshold(
                    score, threshold, adaptive_threshold, all_scores
                )
                
                # Skip irrelevant sections based on threshold
                if score < effective_threshold:
                    logger.debug(f"Skipping result with score {score:.3f} < threshold {effective_threshold:.3f}")
                    continue
                
                metadata = match.get('metadata', {})
                text = metadata.get('text', '')
                
                # Calculate structural rank
                structural_rank = self.calculate_structural_rank(text, query)
                
                # Create result object
                result = {
                    "doc_id": metadata.get('doc_id', ''),
                    "doc_title": metadata.get('doc_title', ''),
                    "text": text,
                    "similarity_score": float(score),
                    "structural_rank": structural_rank,
                    "section_title": metadata.get('section_title', ''),
                    "page_number": metadata.get('page_number', -1),
                    "chunk_id": metadata.get('chunk_id', ''),
                    "word_count": metadata.get('word_count', 0),
                    "legal_density": metadata.get('legal_density', 0),
                    "vector_id": match.get('id', ''),
                    "threshold_used": effective_threshold
                }
                
                results.append(result)
            
            # Step 5: Apply minimum results requirement
            if len(results) < settings.MIN_RESULTS_REQUIRED and all_scores:
                # Lower threshold to get minimum required results
                min_score = min(all_scores)
                adjusted_threshold = min(min_score, threshold * 0.5)
                
                logger.info(f"Adjusting threshold from {threshold:.3f} to {adjusted_threshold:.3f} to meet minimum results requirement")
                
                # Re-process with lower threshold
                results = []
                for match in search_results['matches']:
                    score = match.get('score', 0)
                    if score >= adjusted_threshold:
                        metadata = match.get('metadata', {})
                        text = metadata.get('text', '')
                        structural_rank = self.calculate_structural_rank(text, query)
                        
                        result = {
                            "doc_id": metadata.get('doc_id', ''),
                            "doc_title": metadata.get('doc_title', ''),
                            "text": text,
                            "similarity_score": float(score),
                            "structural_rank": structural_rank,
                            "section_title": metadata.get('section_title', ''),
                            "page_number": metadata.get('page_number', -1),
                            "chunk_id": metadata.get('chunk_id', ''),
                            "word_count": metadata.get('word_count', 0),
                            "legal_density": metadata.get('legal_density', 0),
                            "vector_id": match.get('id', ''),
                            "threshold_used": adjusted_threshold
                        }
                        results.append(result)
            
            # Step 6: Sort by structural rank first, then by similarity score
            results.sort(key=lambda x: (x["structural_rank"], -x["similarity_score"]))
            
            # Step 7: Apply keyword anchoring backup if no results
            if not results and settings.ENABLE_KEYWORD_ANCHORING:
                logger.info("No semantic results found, applying keyword anchoring backup")
                keyword_results = self._apply_keyword_anchoring_backup(
                    query=query,
                    search_results=search_results,
                    return_count=return_count,
                    filter_dict=filter_dict
                )
                if keyword_results:
                    logger.info(f"Keyword anchoring found {len(keyword_results)} backup results")
                    return keyword_results
            
            # Step 8: Return top results
            final_results = results[:return_count]
            
            logger.info(f"Retrieved {len(final_results)} documents from {len(results)} candidates")
            for i, result in enumerate(final_results):
                logger.debug(f"Result {i+1}: Rank={result['structural_rank']}, "
                           f"Score={result['similarity_score']:.3f}, "
                           f"Threshold={result.get('threshold_used', threshold):.3f}, "
                           f"Doc={result['doc_title']}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error in advanced retrieval: {e}")
            return []
    
    def _calculate_effective_threshold(
        self, 
        score: float, 
        base_threshold: float, 
        adaptive: bool, 
        all_scores: List[float]
    ) -> float:
        """
        Calculate effective threshold based on various factors with enhanced logic
        
        Args:
            score: Current similarity score
            base_threshold: Base threshold value
            adaptive: Whether to use adaptive threshold
            all_scores: List of all scores for context
            
        Returns:
            Effective threshold value
        """
        if not adaptive:
            return base_threshold
        
        # Start with base threshold
        effective_threshold = base_threshold
        
        # Enhanced adaptive logic based on score distribution
        if all_scores and len(all_scores) > 1:
            max_score = max(all_scores)
            min_score = min(all_scores)
            score_range = max_score - min_score
            mean_score = sum(all_scores) / len(all_scores)
            
            # Calculate score variance to understand distribution
            variance = sum((s - mean_score) ** 2 for s in all_scores) / len(all_scores)
            std_dev = variance ** 0.5
            
            # Adaptive threshold based on score characteristics
            if score_range > 0.4:  # Wide range of scores
                # Be more selective when we have good options
                if max_score > settings.HIGH_SIMILARITY_THRESHOLD:
                    effective_threshold = max(effective_threshold, mean_score + std_dev * 0.5)
                else:
                    effective_threshold = max(effective_threshold, min_score + score_range * 0.25)
            
            elif score_range < 0.2:  # Narrow range of scores
                # Be more lenient when all scores are similar
                effective_threshold = min(effective_threshold, mean_score - std_dev * 0.5)
            
            # Adjust based on current score position
            if score > settings.HIGH_SIMILARITY_THRESHOLD:
                # High-quality match - can be more selective
                effective_threshold = max(effective_threshold, settings.MEDIUM_SIMILARITY_THRESHOLD)
            elif score < settings.MIN_SIMILARITY_THRESHOLD:
                # Low-quality match - be more lenient
                effective_threshold = min(effective_threshold, settings.MIN_SIMILARITY_THRESHOLD)
            else:
                # Medium-quality match - use percentile-based approach
                sorted_scores = sorted(all_scores)
                score_percentile = sorted_scores.index(score) / len(sorted_scores)
                if score_percentile > 0.7:  # Top 30% of scores
                    effective_threshold = max(effective_threshold, score - 0.1)
                else:
                    effective_threshold = min(effective_threshold, score + 0.05)
        
        # Ensure threshold is within reasonable bounds
        effective_threshold = max(settings.MIN_SIMILARITY_THRESHOLD, 
                                min(effective_threshold, settings.HIGH_SIMILARITY_THRESHOLD))
        
        # Log threshold adjustment for debugging
        if effective_threshold != base_threshold:
            logger.debug(f"Threshold adjusted from {base_threshold:.3f} to {effective_threshold:.3f} "
                        f"(score: {score:.3f}, adaptive: {adaptive})")
        
        return effective_threshold
    
    def _apply_keyword_anchoring_backup(
        self,
        query: str,
        search_results: Dict[str, Any],
        return_count: int,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Apply keyword anchoring backup when semantic search fails
        
        Args:
            query: Original search query
            search_results: Results from semantic search
            return_count: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of keyword-anchored results
        """
        try:
            # Extract keywords from query
            query_keywords = self._extract_keywords_from_query(query)
            if not query_keywords:
                logger.warning("No keywords extracted from query for anchoring backup")
                return []
            
            logger.info(f"Applying keyword anchoring with keywords: {query_keywords}")
            
            # Get all available documents for keyword search
            all_documents = self._get_all_documents_for_keyword_search(filter_dict)
            if not all_documents:
                logger.warning("No documents available for keyword anchoring")
                return []
            
            # Search for keyword matches
            keyword_results = []
            for doc in all_documents:
                text = doc.get('text', '').lower()
                doc_id = doc.get('doc_id', '')
                
                # Check for keyword matches
                matched_keywords = []
                for keyword in query_keywords:
                    if keyword.lower() in text:
                        matched_keywords.append(keyword)
                
                if matched_keywords:
                    # Calculate keyword relevance score
                    keyword_score = self._calculate_keyword_relevance_score(
                        text=text,
                        matched_keywords=matched_keywords,
                        query_keywords=query_keywords
                    )
                    
                    # Create result object
                    result = {
                        "doc_id": doc.get('doc_id', ''),
                        "doc_title": doc.get('doc_title', ''),
                        "text": doc.get('text', ''),
                        "similarity_score": keyword_score,  # Use keyword score as similarity
                        "structural_rank": 1,  # High priority for keyword matches
                        "section_title": doc.get('section_title', ''),
                        "page_number": doc.get('page_number', -1),
                        "chunk_id": doc.get('chunk_id', ''),
                        "word_count": doc.get('word_count', 0),
                        "legal_density": doc.get('legal_density', 0),
                        "vector_id": doc.get('vector_id', ''),
                        "threshold_used": 0.0,  # No threshold for keyword anchoring
                        "keyword_matches": matched_keywords,
                        "retrieval_method": "keyword_anchoring"
                    }
                    
                    keyword_results.append(result)
                    
                    # Break if we have enough results
                    if len(keyword_results) >= settings.MAX_KEYWORD_RESULTS:
                        break
            
            # Sort by keyword relevance score
            keyword_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            logger.info(f"Keyword anchoring found {len(keyword_results)} results")
            return keyword_results[:return_count]
            
        except Exception as e:
            logger.error(f"Error in keyword anchoring backup: {e}")
            return []
    
    def _extract_keywords_from_query(self, query: str) -> List[str]:
        """
        Extract relevant keywords from the query for anchoring
        
        Args:
            query: Search query
            
        Returns:
            List of extracted keywords
        """
        query_lower = query.lower()
        extracted_keywords = []
        
        # Extract keywords from legal categories
        for category, keywords in self.legal_keywords.items():
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    extracted_keywords.append(keyword)
        
        # Extract common legal terms
        legal_terms = [
            "pre-existing disease", "exclusion", "coverage", "claim", "deductible",
            "premium", "waiting period", "renewal", "termination", "policy",
            "insurance", "medical", "hospitalization", "treatment", "expenses"
        ]
        
        for term in legal_terms:
            if term.lower() in query_lower:
                extracted_keywords.append(term)
        
        # Extract individual words that might be relevant
        words = query_lower.split()
        relevant_words = [
            "disease", "exclusion", "coverage", "claim", "deductible", "premium",
            "waiting", "renewal", "termination", "policy", "insurance", "medical",
            "hospital", "treatment", "expense", "limit", "amount", "period"
        ]
        
        for word in words:
            if word in relevant_words and word not in extracted_keywords:
                extracted_keywords.append(word)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in extracted_keywords:
            if keyword.lower() not in seen:
                seen.add(keyword.lower())
                unique_keywords.append(keyword)
        
        return unique_keywords
    
    def _get_all_documents_for_keyword_search(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get all available documents for keyword search
        
        Args:
            filter_dict: Optional filter criteria
            
        Returns:
            List of all available documents
        """
        try:
            # For now, we'll use the existing search results if available
            # In a full implementation, this would fetch all documents from the database
            # or use a broader semantic search with very low threshold
            
            # Use a very low threshold to get more documents for keyword search
            dummy_vector = [0.0] * 1024  # Dummy vector for broad search
            broad_search_results = query_embeddings(
                query_vector=dummy_vector,
                top_k=100,  # Get more documents for keyword search
                filter_dict=filter_dict
            )
            
            if not broad_search_results or 'matches' not in broad_search_results:
                return []
            
            documents = []
            for match in broad_search_results['matches']:
                metadata = match.get('metadata', {})
                document = {
                    "doc_id": metadata.get('doc_id', ''),
                    "doc_title": metadata.get('doc_title', ''),
                    "text": metadata.get('text', ''),
                    "section_title": metadata.get('section_title', ''),
                    "page_number": metadata.get('page_number', -1),
                    "chunk_id": metadata.get('chunk_id', ''),
                    "word_count": metadata.get('word_count', 0),
                    "legal_density": metadata.get('legal_density', 0),
                    "vector_id": match.get('id', '')
                }
                documents.append(document)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting documents for keyword search: {e}")
            return []
    
    def _calculate_keyword_relevance_score(
        self,
        text: str,
        matched_keywords: List[str],
        query_keywords: List[str]
    ) -> float:
        """
        Calculate relevance score based on keyword matches
        
        Args:
            text: Document text
            matched_keywords: Keywords found in the text
            query_keywords: All keywords from the query
            
        Returns:
            Relevance score between 0 and 1
        """
        if not matched_keywords or not query_keywords:
            return 0.0
        
        # Calculate keyword density
        text_words = text.split()
        keyword_count = sum(text.count(keyword.lower()) for keyword in matched_keywords)
        keyword_density = keyword_count / len(text_words) if text_words else 0.0
        
        # Calculate keyword coverage (percentage of query keywords found)
        keyword_coverage = len(matched_keywords) / len(query_keywords)
        
        # Calculate position bonus (keywords near the beginning get higher score)
        position_bonus = 0.0
        text_lower = text.lower()
        for keyword in matched_keywords:
            keyword_pos = text_lower.find(keyword.lower())
            if keyword_pos >= 0:
                # Normalize position (0 = beginning, 1 = end)
                normalized_pos = keyword_pos / len(text_lower)
                position_bonus += (1.0 - normalized_pos) * 0.2  # Max 0.2 bonus per keyword
        
        # Combine scores
        relevance_score = (
            keyword_density * 0.4 +
            keyword_coverage * 0.4 +
            position_bonus * 0.2
        )
        
        # Ensure score is between 0 and 1
        return min(1.0, max(0.0, relevance_score))
    
    def get_legal_keywords(self) -> Dict[str, List[str]]:
        """
        Get the legal keywords used for structural ranking
        
        Returns:
            Dictionary of legal keyword categories
        """
        return self.legal_keywords.copy()
    
    def add_legal_keywords(self, category: str, keywords: List[str]):
        """
        Add new legal keywords for structural ranking
        
        Args:
            category: Category name for the keywords
            keywords: List of keywords to add
        """
        if category not in self.legal_keywords:
            self.legal_keywords[category] = []
        self.legal_keywords[category].extend(keywords)
        logger.info(f"Added {len(keywords)} keywords to category '{category}'")
    
    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze the intent of a query based on legal keywords
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with intent analysis
        """
        query_lower = query.lower()
        intent_analysis = {
            "primary_category": None,
            "secondary_categories": [],
            "confidence": 0.0,
            "keywords_found": []
        }
        
        category_scores = {}
        
        for category, keywords in self.legal_keywords.items():
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
                    found_keywords.append(keyword)
            
            if score > 0:
                category_scores[category] = score
                intent_analysis["keywords_found"].extend(found_keywords)
        
        if category_scores:
            # Find primary category (highest score)
            primary_category = max(category_scores, key=category_scores.get)
            intent_analysis["primary_category"] = primary_category
            
            # Find secondary categories (other categories with scores)
            secondary_categories = [cat for cat, score in category_scores.items() 
                                  if cat != primary_category and score > 0]
            intent_analysis["secondary_categories"] = secondary_categories
            
            # Calculate confidence based on keyword density
            total_keywords = len(intent_analysis["keywords_found"])
            intent_analysis["confidence"] = min(1.0, total_keywords / 3.0)  # Normalize to 0-1
        
        return intent_analysis

# Global instance
advanced_retrieval_engine = AdvancedRetrievalEngine()

def retrieve_documents_advanced(
    query: str,
    top_k: int = 10,
    threshold: float = 0.25,
    filter_dict: Optional[Dict[str, Any]] = None,
    return_count: int = 3,
    adaptive_threshold: bool = True
) -> List[Dict[str, Any]]:
    """
    Convenience function for advanced document retrieval
    
    Args:
        query: Search query
        top_k: Number of initial semantic results to consider
        threshold: Similarity threshold for filtering
        filter_dict: Optional filter criteria
        return_count: Number of final results to return
        adaptive_threshold: Whether to use adaptive threshold adjustment
        
    Returns:
        List of ranked document results
    """
    return advanced_retrieval_engine.retrieve_documents(
        query=query,
        top_k=top_k,
        threshold=threshold,
        filter_dict=filter_dict,
        return_count=return_count,
        adaptive_threshold=adaptive_threshold
    )

def analyze_query_intent(query: str) -> Dict[str, Any]:
    """
    Convenience function for query intent analysis
    
    Args:
        query: Search query
        
    Returns:
        Dictionary with intent analysis
    """
    return advanced_retrieval_engine.analyze_query_intent(query) 