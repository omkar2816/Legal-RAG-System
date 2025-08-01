"""
Query enhancement utilities for legal RAG system
"""
import re
from typing import List, Dict, Any, Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class LegalQueryEnhancer:
    """Enhance legal queries for better retrieval accuracy"""
    
    def __init__(self):
        # Legal terminology mappings
        self.legal_synonyms = {
            # Insurance terms
            "waiting period": ["exclusion period", "waiting time", "time limit", "period before coverage"],
            "pre-existing": ["pre-existing", "existing", "prior", "pre-existing condition"],
            "coverage": ["cover", "protection", "insurance", "benefit"],
            "exclusion": ["not covered", "excluded", "limitation", "restriction"],
            "claim": ["claim", "request", "application", "notification"],
            "policy": ["policy", "contract", "agreement", "document"],
            
            # Legal terms
            "termination": ["termination", "cancellation", "ending", "discontinuation"],
            "liability": ["liability", "responsibility", "obligation", "duty"],
            "indemnification": ["indemnification", "compensation", "reimbursement", "payment"],
            "confidentiality": ["confidentiality", "privacy", "secrecy", "non-disclosure"],
            "breach": ["breach", "violation", "infringement", "non-compliance"],
            
            # Time-related terms
            "month": ["month", "months", "30 days", "calendar month"],
            "year": ["year", "years", "12 months", "annual"],
            "day": ["day", "days", "24 hours", "daily"],
            "period": ["period", "duration", "timeframe", "term"],
            
            # Amount-related terms
            "amount": ["amount", "sum", "value", "figure", "total"],
            "maximum": ["maximum", "max", "highest", "upper limit", "cap"],
            "minimum": ["minimum", "min", "lowest", "lower limit", "floor"],
            "percentage": ["percentage", "percent", "%", "rate", "proportion"]
        }
        
        # Insurance-specific terms
        self.insurance_terms = {
            "health": ["health", "medical", "healthcare", "treatment"],
            "hospitalization": ["hospitalization", "hospital", "inpatient", "admission"],
            "outpatient": ["outpatient", "clinic", "ambulatory", "day care"],
            "surgery": ["surgery", "surgical", "operation", "procedure"],
            "medication": ["medication", "medicine", "drug", "prescription"],
            "diagnosis": ["diagnosis", "diagnostic", "test", "examination"],
            "treatment": ["treatment", "therapy", "care", "management"]
        }
        
        # Query intent patterns
        self.intent_patterns = {
            "definition": [
                r"what is\s+(\w+)",
                r"define\s+(\w+)",
                r"meaning of\s+(\w+)",
                r"explain\s+(\w+)"
            ],
            "procedure": [
                r"how to\s+(\w+)",
                r"process for\s+(\w+)",
                r"steps to\s+(\w+)",
                r"procedure for\s+(\w+)"
            ],
            "limitation": [
                r"what are the limits",
                r"maximum\s+(\w+)",
                r"minimum\s+(\w+)",
                r"restrictions on\s+(\w+)",
                r"limitations of\s+(\w+)"
            ],
            "exclusion": [
                r"what is not covered",
                r"exclusions",
                r"not covered",
                r"what is excluded",
                r"limitations"
            ],
            "time_period": [
                r"how long",
                r"duration",
                r"period",
                r"time limit",
                r"waiting period",
                r"when"
            ],
            "amount": [
                r"how much",
                r"amount",
                r"cost",
                r"price",
                r"sum",
                r"value"
            ]
        }
    
    def enhance_query(self, query: str) -> str:
        """
        Enhance a legal query with synonyms and related terms
        
        Args:
            query: Original query
            
        Returns:
            Enhanced query
        """
        enhanced = query.lower().strip()
        
        # Add synonyms for key terms
        for term, synonyms in self.legal_synonyms.items():
            if term in enhanced:
                # Add synonyms to the query
                enhanced += " " + " ".join(synonyms[:2])  # Add top 2 synonyms
        
        # Add insurance-specific terms if relevant
        for category, terms in self.insurance_terms.items():
            if any(term in enhanced for term in terms):
                enhanced += " " + " ".join(terms[:2])
        
        # Clean up the enhanced query
        enhanced = re.sub(r'\s+', ' ', enhanced)  # Remove extra spaces
        enhanced = enhanced.strip()
        
        logger.debug(f"Query enhanced: '{query}' -> '{enhanced}'")
        return enhanced
    
    def classify_intent(self, query: str) -> Dict[str, Any]:
        """
        Classify the intent of a legal query
        
        Args:
            query: Query to classify
            
        Returns:
            Intent classification with confidence
        """
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            intent_scores[intent] = score
        
        # Find the highest scoring intent
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[primary_intent] / max(intent_scores.values()) if max(intent_scores.values()) > 0 else 0
        else:
            primary_intent = "general"
            confidence = 0.0
        
        return {
            "primary_intent": primary_intent,
            "confidence": confidence,
            "all_scores": intent_scores
        }
    
    def expand_query(self, query: str) -> List[str]:
        """
        Generate multiple query variations for better retrieval
        
        Args:
            query: Original query
            
        Returns:
            List of query variations
        """
        variations = [query]
        
        # Add enhanced version
        enhanced = self.enhance_query(query)
        if enhanced != query.lower():
            variations.append(enhanced)
        
        # Generate variations based on intent
        intent = self.classify_intent(query)
        
        if intent["primary_intent"] == "time_period":
            # Add time-related variations
            time_variations = [
                query.replace("how long", "duration"),
                query.replace("how long", "period"),
                query.replace("how long", "time limit"),
                query.replace("waiting period", "exclusion period"),
                query.replace("waiting period", "time before coverage")
            ]
            variations.extend([v for v in time_variations if v != query])
        
        elif intent["primary_intent"] == "amount":
            # Add amount-related variations
            amount_variations = [
                query.replace("how much", "amount"),
                query.replace("how much", "maximum"),
                query.replace("how much", "value"),
                query.replace("cost", "amount"),
                query.replace("price", "amount")
            ]
            variations.extend([v for v in amount_variations if v != query])
        
        elif intent["primary_intent"] == "definition":
            # Add definition-related variations
            def_variations = [
                query.replace("what is", "define"),
                query.replace("what is", "explain"),
                query.replace("meaning of", "definition of"),
                query.replace("explain", "what is")
            ]
            variations.extend([v for v in def_variations if v != query])
        
        # Remove duplicates and return
        unique_variations = list(dict.fromkeys(variations))
        logger.debug(f"Generated {len(unique_variations)} query variations")
        
        return unique_variations
    
    def normalize_query(self, query: str) -> str:
        """
        Normalize query for consistent processing
        
        Args:
            query: Query to normalize
            
        Returns:
            Normalized query
        """
        # Convert to lowercase
        normalized = query.lower()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove punctuation that might interfere with search
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Clean up whitespace again
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract important keywords from query
        
        Args:
            query: Query to extract keywords from
            
        Returns:
            List of important keywords
        """
        # Normalize query
        normalized = self.normalize_query(query)
        
        # Split into words
        words = normalized.split()
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'what', 'when', 'where', 'why', 'how'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def create_search_queries(self, query: str) -> List[str]:
        """
        Create multiple search queries for comprehensive retrieval
        
        Args:
            query: Original query
            
        Returns:
            List of search queries to try
        """
        queries = []
        
        # Original query
        queries.append(query)
        
        # Enhanced query
        enhanced = self.enhance_query(query)
        if enhanced != query.lower():
            queries.append(enhanced)
        
        # Query variations
        variations = self.expand_query(query)
        queries.extend(variations)
        
        # Keyword-based queries
        keywords = self.extract_keywords(query)
        if len(keywords) >= 3:
            # Create keyword combinations
            keyword_query = " ".join(keywords[:3])  # Top 3 keywords
            queries.append(keyword_query)
        
        # Remove duplicates and limit to reasonable number
        unique_queries = list(dict.fromkeys(queries))[:5]  # Max 5 queries
        
        logger.info(f"Created {len(unique_queries)} search queries for: '{query}'")
        return unique_queries

    def detect_multiple_questions(self, query: str) -> List[str]:
        """
        Detect if a query contains multiple questions and split them
        
        Args:
            query: Input query that may contain multiple questions
            
        Returns:
            List of individual questions
        """
        try:
            # Ensure query is a string
            if not isinstance(query, str):
                logger.warning(f"detect_multiple_questions received non-string input: {type(query)} - {query}")
                return [str(query)] if query else [""]
            
            # Handle empty or None query
            if not query or not query.strip():
                return [""]
            
            query = query.strip()
            
            # Simple approach: split by common separators
            questions = []
            
            # Split by comma followed by space and word
            if ',' in query:
                parts = query.split(',')
                for part in parts:
                    part = part.strip()
                    if part and len(part) > 3:  # Minimum length
                        # Ensure it ends with question mark
                        if not part.endswith('?'):
                            part += '?'
                        questions.append(part)
            
            # If no comma splitting worked, try semicolon
            if not questions and ';' in query:
                parts = query.split(';')
                for part in parts:
                    part = part.strip()
                    if part and len(part) > 3:
                        if not part.endswith('?'):
                            part += '?'
                        questions.append(part)
            
            # If still no questions, try splitting by "and"
            if not questions and ' and ' in query.lower():
                parts = query.split(' and ')
                for part in parts:
                    part = part.strip()
                    if part and len(part) > 3:
                        if not part.endswith('?'):
                            part += '?'
                        questions.append(part)
            
            # If still no questions, try splitting by multiple question marks
            if not questions and query.count('?') > 1:
                # Split by question marks
                parts = query.split('?')
                for i, part in enumerate(parts[:-1]):  # Skip the last empty part
                    part = part.strip()
                    if part and len(part) > 3:
                        questions.append(part + '?')
            
            # If we still have no questions, return the original query
            if not questions:
                # Ensure original query ends with question mark
                if not query.endswith('?'):
                    query += '?'
                return [query]
            
            # Clean up questions
            cleaned_questions = []
            for q in questions:
                q = q.strip()
                if q and len(q) > 3:  # Minimum question length
                    # Ensure question ends with proper punctuation
                    if not q.endswith('?'):
                        q += '?'
                    cleaned_questions.append(q)
            
            # Always return a list, even if it's just the original query
            if not cleaned_questions:
                if not query.endswith('?'):
                    query += '?'
                return [query]
            else:
                return cleaned_questions
                
        except Exception as e:
            logger.error(f"Error in LegalQueryEnhancer.detect_multiple_questions: {e}")
            logger.error(f"Query that caused error: {query}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Fallback to original query
            if query and not query.endswith('?'):
                query += '?'
            return [str(query)] if query else [""]
    
    def enhance_multiple_questions(self, query: str) -> str:
        """
        Enhance a query that may contain multiple questions
        
        Args:
            query: Query that may contain multiple questions
            
        Returns:
            Enhanced query with better structure for multiple questions
        """
        questions = self.detect_multiple_questions(query)
        
        if len(questions) == 1:
            # Single question, use normal enhancement
            return self.enhance_query(query)
        
        # Multiple questions detected
        enhanced_questions = []
        for i, question in enumerate(questions, 1):
            enhanced = self.enhance_query(question)
            enhanced_questions.append(f"{i}. {enhanced}")
        
        # Combine with clear structure
        combined = f"Please answer the following questions comprehensively:\n\n" + "\n\n".join(enhanced_questions)
        
        return combined

# Global instance
query_enhancer = LegalQueryEnhancer()

# Convenience functions
def enhance_legal_query(query: str) -> str:
    """Convenience function for query enhancement"""
    return query_enhancer.enhance_query(query)

def classify_query_intent(query: str) -> Dict[str, Any]:
    """Convenience function for intent classification"""
    return query_enhancer.classify_intent(query)

def expand_legal_query(query: str) -> List[str]:
    """Convenience function for query expansion"""
    return query_enhancer.expand_query(query)

def create_search_queries(query: str) -> List[str]:
    """Convenience function for creating search queries"""
    return query_enhancer.create_search_queries(query)

def detect_multiple_questions(query: str) -> List[str]:
    """Convenience function for detecting multiple questions"""
    try:
        # Ensure input is a string
        if not isinstance(query, str):
            logger.warning(f"detect_multiple_questions received non-string input: {type(query)} - {query}")
            return [str(query)] if query else [""]
        
        # Handle empty or None query
        if not query or not query.strip():
            return [""]
        
        # Call the actual detection function
        logger.debug(f"Calling query_enhancer.detect_multiple_questions with: {repr(query)}")
        result = query_enhancer.detect_multiple_questions(query)
        logger.debug(f"query_enhancer.detect_multiple_questions returned: {type(result)} - {result}")
        
        # Ensure result is a list
        if isinstance(result, list):
            # Validate that all items in the list are strings
            validated_result = []
            for i, item in enumerate(result):
                if isinstance(item, str):
                    validated_result.append(item)
                else:
                    logger.warning(f"Non-string item at index {i}: {type(item)} - {item}")
                    validated_result.append(str(item))
            logger.debug(f"Final validated result: {validated_result}")
            return validated_result
        elif isinstance(result, (str, bool, int, float)):
            # If it's a primitive type, wrap it in a list
            logger.warning(f"detect_multiple_questions returned {type(result)} instead of list: {result}")
            return [str(result)]
        else:
            # Fallback to original query
            logger.warning(f"detect_multiple_questions returned unexpected type {type(result)}: {result}")
            return [str(query)] if query else [""]
            
    except Exception as e:
        # Log the error and fallback
        logger.error(f"Error in detect_multiple_questions: {e}")
        logger.error(f"Query that caused error: {query}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return [str(query)] if query else [""]

def enhance_multiple_questions(query: str) -> str:
    """Convenience function for enhancing multiple questions"""
    return query_enhancer.enhance_multiple_questions(query) 