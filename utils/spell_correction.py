"""Spell correction utilities for the Legal RAG System"""
import re
from typing import List, Dict, Any, Optional
import logging
from difflib import get_close_matches

logger = logging.getLogger(__name__)

class SpellCorrector:
    """Utility class for spell correction of legal queries"""
    
    def __init__(self):
        # Common legal and insurance terms dictionary
        self.legal_terms = {
            # Insurance terms
            "preexisting": "pre-existing",
            "preexisting disease": "pre-existing disease",
            "preexisting condition": "pre-existing condition",
            "pre existing": "pre-existing",
            "pre existing disease": "pre-existing disease",
            "pre existing condition": "pre-existing condition",
            "deductable": "deductible",
            "deductibles": "deductible",
            "copay": "co-pay",
            "copays": "co-pays",
            "copayment": "co-payment",
            "copayments": "co-payments",
            "hospitilization": "hospitalization",
            "hospitilizations": "hospitalizations",
            "surgury": "surgery",
            "surgeries": "surgeries",
            "exclusions": "exclusion",
            "exclusionary": "exclusion",
            "benifits": "benefits",
            "benifit": "benefit",
            "cancelation": "cancellation",
            "cancelations": "cancellations",
            "premiums": "premium",
            "policys": "policies",
            "policy's": "policies",
            "clause": "clause",
            "clauses": "clauses",
            "coverage": "coverage",
            "coverages": "coverages",
            "claim": "claim",
            "claims": "claims",
            "claimant": "claimant",
            "claimants": "claimants",
            "insured": "insured",
            "insureds": "insureds",
            "insurer": "insurer",
            "insurers": "insurers",
            "policy": "policy",
            "policies": "policies",
            "premium": "premium",
            "premiums": "premiums",
            "renewal": "renewal",
            "renewals": "renewals",
            "termination": "termination",
            "terminations": "terminations",
            "waiting period": "waiting period",
            "waiting periods": "waiting periods",
            "knee surgury": "knee surgery",
            "knee replacement": "knee replacement",
            "knee replacements": "knee replacements",
            "knee surgeries": "knee surgeries",
            "knee operation": "knee operation",
            "knee operations": "knee operations",
            "knee procedure": "knee procedure",
            "knee procedures": "knee procedures"
        }
        
        # Build a comprehensive dictionary of all terms
        self.all_terms = {}
        self.all_terms.update(self.legal_terms)
        
        # Create a list of all terms for fuzzy matching
        self.term_list = list(self.all_terms.keys()) + list(self.all_terms.values())
        self.term_list = list(set(self.term_list))  # Remove duplicates
    
    def correct_query(self, query: str) -> Dict[str, Any]:
        """
        Apply spell correction to a query
        
        Args:
            query: Original query string
            
        Returns:
            Dictionary with corrected query and correction metadata
        """
        if not query or not query.strip():
            return {
                "corrected_query": query,
                "original_query": query,
                "corrections_made": False,
                "corrections": []
            }
        
        original_query = query
        corrections = []
        
        # Normalize query for processing
        query = query.lower().strip()
        
        # First check for exact matches in legal terms dictionary
        for term, correction in self.legal_terms.items():
            if term in query and term != correction:
                query = query.replace(term, correction)
                corrections.append({
                    "original": term,
                    "corrected": correction,
                    "method": "exact_match"
                })
        
        # Then check for fuzzy matches on individual words
        words = re.findall(r'\b\w+\b', query)
        for i, word in enumerate(words):
            # Skip short words and already corrected words
            if len(word) <= 3 or any(c["original"] == word for c in corrections):
                continue
            
            # Try to find close matches
            close_matches = get_close_matches(word, self.term_list, n=1, cutoff=0.8)
            if close_matches and close_matches[0] != word:
                # Replace the word in the query
                query = re.sub(r'\b' + re.escape(word) + r'\b', close_matches[0], query)
                corrections.append({
                    "original": word,
                    "corrected": close_matches[0],
                    "method": "fuzzy_match",
                    "confidence": 0.8  # Default confidence for fuzzy matches
                })
        
        # Check for multi-word terms that might have been missed
        for term, correction in self.legal_terms.items():
            if ' ' in term and term in query and term != correction:
                query = query.replace(term, correction)
                corrections.append({
                    "original": term,
                    "corrected": correction,
                    "method": "multi_word_match"
                })
        
        # Return the corrected query and metadata
        return {
            "corrected_query": query,
            "original_query": original_query,
            "corrections_made": len(corrections) > 0,
            "corrections": corrections
        }
    
    def suggest_corrections(self, query: str) -> List[Dict[str, Any]]:
        """
        Suggest possible corrections for a query without applying them
        
        Args:
            query: Original query string
            
        Returns:
            List of possible corrections with confidence scores
        """
        if not query or not query.strip():
            return []
        
        suggestions = []
        query = query.lower().strip()
        
        # Check for exact matches in legal terms dictionary
        for term, correction in self.legal_terms.items():
            if term in query and term != correction:
                suggestions.append({
                    "original": term,
                    "suggested": correction,
                    "confidence": 1.0,
                    "method": "exact_match"
                })
        
        # Check for fuzzy matches on individual words
        words = re.findall(r'\b\w+\b', query)
        for word in words:
            # Skip short words
            if len(word) <= 3:
                continue
            
            # Try to find close matches
            close_matches = get_close_matches(word, self.term_list, n=3, cutoff=0.7)
            for i, match in enumerate(close_matches):
                if match != word:
                    # Calculate confidence based on position in matches
                    confidence = 0.9 if i == 0 else (0.8 if i == 1 else 0.7)
                    suggestions.append({
                        "original": word,
                        "suggested": match,
                        "confidence": confidence,
                        "method": "fuzzy_match"
                    })
        
        return suggestions

# Global spell corrector instance
spell_corrector = SpellCorrector()

# Convenience functions
def correct_query(query: str) -> Dict[str, Any]:
    """Convenience function for query spell correction"""
    return spell_corrector.correct_query(query)

def suggest_corrections(query: str) -> List[Dict[str, Any]]:
    """Convenience function for suggesting query corrections"""
    return spell_corrector.suggest_corrections(query)