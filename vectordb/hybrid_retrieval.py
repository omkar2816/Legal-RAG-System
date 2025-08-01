"""
Hybrid retrieval system combining semantic and keyword search
"""
import re
from typing import List, Dict, Any, Optional
from config.settings import settings
import logging
from utils.query_enhancer import query_enhancer, create_search_queries
from vectordb.pinecone_client import query_embeddings, get_all_vectors

logger = logging.getLogger(__name__)

class HybridRetrievalEngine:
    """Hybrid retrieval combining semantic and keyword search"""
    
    def __init__(self):
        self.semantic_weight = 0.7
        self.keyword_weight = 0.3
        self.min_confidence = 0.4
        self.max_keyword_search_vectors = 1000  # Limit for keyword search
        
    def hybrid_search(
        self, 
        query: str, 
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword approaches
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of ranked results
        """
        try:
            # Step 1: Generate multiple search queries
            search_queries = create_search_queries(query)
            
            # Step 2: Perform semantic search for each query
            semantic_results = []
            for search_query in search_queries:
                results = self._semantic_search(search_query, top_k * 2, filter_dict)
                semantic_results.extend(results)
            
            # Step 3: Perform keyword search (only if enabled and efficient)
            keyword_results = []
            if settings.ENABLE_HYBRID_SEARCH:
                keyword_results = self._keyword_search(query, top_k * 2, filter_dict)
            
            # Step 4: Combine and rank results
            combined_results = self._combine_results(
                semantic_results, 
                keyword_results, 
                top_k
            )
            
            # Step 5: Apply confidence filtering
            filtered_results = self._filter_by_confidence(combined_results)
            
            logger.info(f"Hybrid search completed: {len(filtered_results)} results")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []
    
    def _semantic_search(
        self, 
        query: str, 
        top_k: int,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using embeddings
        
        Args:
            query: Search query
            top_k: Number of results
            filter_dict: Optional filter criteria
            
        Returns:
            List of semantic search results
        """
        try:
            # Get query embedding
            from embeddings.embed_client import embedding_client
            query_vector = embedding_client.get_embeddings([query])[0]
            
            # Search in vector database
            search_results = query_embeddings(
                query_vector=query_vector,
                top_k=top_k,
                filter_dict=filter_dict
            )
            
            if not search_results or 'matches' not in search_results:
                return []
            
            # Convert to standard format
            results = []
            for match in search_results['matches']:
                metadata = match.get('metadata', {})
                result = {
                    "doc_id": metadata.get('doc_id', ''),
                    "doc_title": metadata.get('doc_title', ''),
                    "text": metadata.get('text', ''),
                    "similarity_score": match.get('score', 0.0),
                    "search_type": "semantic",
                    "section_title": metadata.get('section_title', ''),
                    "page_number": metadata.get('page_number', -1),
                    "chunk_id": metadata.get('chunk_id', ''),
                    "word_count": metadata.get('word_count', 0),
                    "legal_density": metadata.get('legal_density', 0),
                    "vector_id": match.get('id', ''),
                    "semantic_score": match.get('score', 0.0),
                    "keyword_score": 0.0
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []
    
    def _keyword_search(
        self, 
        query: str, 
        top_k: int,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search
        
        Args:
            query: Search query
            top_k: Number of results
            filter_dict: Optional filter criteria
            
        Returns:
            List of keyword search results
        """
        try:
            # Extract keywords from query
            keywords = query_enhancer.extract_keywords(query)
            
            if not keywords:
                return []
            
            # Get documents with limit to avoid performance issues
            all_documents = get_all_vectors(
                filter_dict=filter_dict, 
                limit=self.max_keyword_search_vectors
            )
            
            if not all_documents:
                logger.warning("No documents found for keyword search")
                return []
            
            # Score documents based on keyword matches
            scored_documents = []
            for doc in all_documents:
                text = doc.get('metadata', {}).get('text', '').lower()
                doc_title = doc.get('metadata', {}).get('doc_title', '').lower()
                section_title = doc.get('metadata', {}).get('section_title', '').lower()
                
                # Calculate keyword score
                keyword_score = self._calculate_keyword_score(
                    text, doc_title, section_title, keywords
                )
                
                if keyword_score > 0:
                    metadata = doc.get('metadata', {})
                    result = {
                        "doc_id": metadata.get('doc_id', ''),
                        "doc_title": metadata.get('doc_title', ''),
                        "text": metadata.get('text', ''),
                        "similarity_score": keyword_score,
                        "search_type": "keyword",
                        "section_title": metadata.get('section_title', ''),
                        "page_number": metadata.get('page_number', -1),
                        "chunk_id": metadata.get('chunk_id', ''),
                        "word_count": metadata.get('word_count', 0),
                        "legal_density": metadata.get('legal_density', 0),
                        "vector_id": doc.get('id', ''),
                        "keyword_matches": self._get_keyword_matches(text, keywords),
                        "semantic_score": 0.0,
                        "keyword_score": keyword_score
                    }
                    scored_documents.append(result)
            
            # Sort by keyword score and return top results
            scored_documents.sort(key=lambda x: x['similarity_score'], reverse=True)
            return scored_documents[:top_k]
            
        except Exception as e:
            logger.error(f"Error in keyword search: {str(e)}")
            return []
    
    def _calculate_keyword_score(
        self, 
        text: str, 
        doc_title: str, 
        section_title: str, 
        keywords: List[str]
    ) -> float:
        """
        Calculate keyword relevance score
        
        Args:
            text: Document text
            doc_title: Document title
            section_title: Section title
            keywords: Search keywords
            
        Returns:
            Keyword relevance score
        """
        score = 0.0
        
        for keyword in keywords:
            # Text matches (weight: 1.0)
            text_matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
            score += text_matches * 1.0
            
            # Title matches (weight: 3.0)
            title_matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', doc_title, re.IGNORECASE))
            score += title_matches * 3.0
            
            # Section title matches (weight: 2.0)
            section_matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', section_title, re.IGNORECASE))
            score += section_matches * 2.0
        
        # Normalize score
        if score > 0:
            score = min(score / 10.0, 1.0)  # Normalize to 0-1 range
        
        return score
    
    def _get_keyword_matches(self, text: str, keywords: List[str]) -> List[str]:
        """
        Get list of keywords that match in the text
        
        Args:
            text: Document text
            keywords: Search keywords
            
        Returns:
            List of matching keywords
        """
        matches = []
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                matches.append(keyword)
        return matches
    
    def _combine_results(
        self, 
        semantic_results: List[Dict], 
        keyword_results: List[Dict], 
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Combine semantic and keyword results
        
        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from keyword search
            top_k: Number of results to return
            
        Returns:
            Combined and ranked results
        """
        # Create a dictionary to track combined results
        combined_dict = {}
        
        # Process semantic results
        for result in semantic_results:
            doc_id = result.get('doc_id', '')
            chunk_id = result.get('chunk_id', '')
            key = f"{doc_id}_{chunk_id}"
            
            if key not in combined_dict:
                combined_dict[key] = result.copy()
                combined_dict[key]['semantic_score'] = result.get('similarity_score', 0.0)
                combined_dict[key]['keyword_score'] = 0.0
            else:
                # Update with better semantic score
                existing_score = combined_dict[key].get('semantic_score', 0.0)
                new_score = result.get('similarity_score', 0.0)
                if new_score > existing_score:
                    combined_dict[key].update(result)
                    combined_dict[key]['semantic_score'] = new_score
        
        # Process keyword results
        for result in keyword_results:
            doc_id = result.get('doc_id', '')
            chunk_id = result.get('chunk_id', '')
            key = f"{doc_id}_{chunk_id}"
            
            if key not in combined_dict:
                combined_dict[key] = result.copy()
                combined_dict[key]['semantic_score'] = 0.0
                combined_dict[key]['keyword_score'] = result.get('similarity_score', 0.0)
            else:
                # Add keyword score to existing result
                combined_dict[key]['keyword_score'] = result.get('similarity_score', 0.0)
                # Update keyword matches if available
                if result.get('keyword_matches'):
                    combined_dict[key]['keyword_matches'] = result.get('keyword_matches')
        
        # Calculate combined scores
        combined_results = []
        for result in combined_dict.values():
            semantic_score = result.get('semantic_score', 0.0)
            keyword_score = result.get('keyword_score', 0.0)
            
            # Calculate weighted combined score
            combined_score = (
                semantic_score * self.semantic_weight + 
                keyword_score * self.keyword_weight
            )
            
            result['combined_score'] = combined_score
            result['similarity_score'] = combined_score  # For compatibility
            combined_results.append(result)
        
        # Sort by combined score and return top results
        combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
        return combined_results[:top_k]
    
    def _filter_by_confidence(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter results by confidence threshold
        
        Args:
            results: List of results to filter
            
        Returns:
            Filtered results
        """
        filtered_results = []
        for result in results:
            combined_score = result.get('combined_score', result.get('similarity_score', 0.0))
            if combined_score >= self.min_confidence:
                filtered_results.append(result)
        
        return filtered_results
    
    def multi_stage_retrieval(
        self, 
        query: str, 
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Multi-stage retrieval pipeline
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional filter criteria
            
        Returns:
            List of ranked results
        """
        try:
            # Stage 1: Broad semantic search
            semantic_results = self._semantic_search(query, top_k * 3, filter_dict)
            
            # Stage 2: Keyword filtering (if enabled)
            keyword_results = []
            if settings.ENABLE_HYBRID_SEARCH:
                keyword_results = self._keyword_search(query, top_k * 2, filter_dict)
            
            # Stage 3: Combine results
            combined_results = self._combine_results(semantic_results, keyword_results, top_k * 2)
            
            # Stage 4: Re-rank with context
            reranked_results = self._rerank_with_context(combined_results, query)
            
            # Stage 5: Final filtering
            final_results = self._filter_by_confidence(reranked_results)
            
            logger.info(f"Multi-stage retrieval completed: {len(final_results)} results")
            return final_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in multi-stage retrieval: {str(e)}")
            return []
    
    def _rerank_with_context(
        self, 
        results: List[Dict[str, Any]], 
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Re-rank results based on query context and intent
        
        Args:
            results: List of results to re-rank
            query: Original query
            
        Returns:
            Re-ranked results
        """
        try:
            # Analyze query intent
            intent_analysis = query_enhancer.classify_intent(query)
            primary_intent = intent_analysis.get('primary_intent', 'general')
            
            for result in results:
                score_boost = 0.0
                
                # Boost based on query intent
                if primary_intent == 'time_period':
                    # Boost results with time-related terms
                    text = result.get('text', '').lower()
                    time_terms = ['period', 'waiting', 'time', 'duration', 'months', 'years', 'days']
                    for term in time_terms:
                        if term in text:
                            score_boost += 0.1
                
                elif primary_intent == 'amount':
                    # Boost results with amount-related terms
                    text = result.get('text', '').lower()
                    amount_terms = ['amount', 'limit', 'coverage', 'sum', 'maximum', 'minimum', 'percentage']
                    for term in amount_terms:
                        if term in text:
                            score_boost += 0.1
                
                elif primary_intent == 'definition':
                    # Boost results with definition-like structure
                    text = result.get('text', '').lower()
                    definition_terms = ['means', 'defined', 'refers to', 'shall mean', 'is defined']
                    for term in definition_terms:
                        if term in text:
                            score_boost += 0.15
                
                # Boost based on structural elements
                section_title = result.get('section_title', '').lower()
                if 'definition' in section_title or 'definitions' in section_title:
                    score_boost += 0.2
                
                if 'exclusion' in section_title or 'exclusions' in section_title:
                    score_boost += 0.15
                
                # Apply score boost
                current_score = result.get('combined_score', result.get('similarity_score', 0.0))
                result['combined_score'] = min(current_score + score_boost, 1.0)
                result['similarity_score'] = result['combined_score']  # For compatibility
            
            # Re-sort by updated scores
            results.sort(key=lambda x: x.get('combined_score', 0.0), reverse=True)
            return results
            
        except Exception as e:
            logger.error(f"Error in context re-ranking: {str(e)}")
            return results

# Global instance
_hybrid_engine = None

def get_hybrid_engine():
    """Get global hybrid retrieval engine instance"""
    global _hybrid_engine
    if _hybrid_engine is None:
        _hybrid_engine = HybridRetrievalEngine()
    return _hybrid_engine

# Convenience functions
def hybrid_search(
    query: str, 
    top_k: int = 10,
    filter_dict: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Convenience function for hybrid search"""
    engine = get_hybrid_engine()
    return engine.hybrid_search(query, top_k, filter_dict)

def multi_stage_retrieval(
    query: str, 
    top_k: int = 10,
    filter_dict: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Convenience function for multi-stage retrieval"""
    engine = get_hybrid_engine()
    return engine.multi_stage_retrieval(query, top_k, filter_dict) 