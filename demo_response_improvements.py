#!/usr/bin/env python3
"""
Demonstration of Response Formatting Improvements
Shows the enhanced response formatting and threshold handling capabilities
"""

import json
from typing import List, Dict, Any

# Simulate the response formatter functionality
class DemoResponseFormatter:
    """Demo version of the response formatter"""
    
    def __init__(self):
        self.response_templates = {
            "direct_answer": {
                "template": "Based on the policy document, {answer}",
                "max_length": 250
            },
            "procedural": {
                "template": "According to the policy procedures: {answer}",
                "max_length": 300
            },
            "exclusion": {
                "template": "Important: {answer}",
                "max_length": 280
            },
            "coverage": {
                "template": "Coverage information: {answer}",
                "max_length": 300
            },
            "claim": {
                "template": "Claim process details: {answer}",
                "max_length": 350
            },
            "general": {
                "template": "{answer}",
                "max_length": 300
            }
        }
    
    def classify_response_type(self, query: str) -> str:
        """Classify the type of response based on query content"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["waiting period", "wait period", "waiting time"]):
            return "direct_answer"
        elif any(term in query_lower for term in ["how to", "process", "procedure", "steps", "submit"]):
            return "procedural"
        elif any(term in query_lower for term in ["exclusion", "not covered", "excluded", "limitation"]):
            return "exclusion"
        elif any(term in query_lower for term in ["coverage", "covered", "benefits", "what is covered"]):
            return "coverage"
        elif any(term in query_lower for term in ["claim", "claiming", "claim process"]):
            return "claim"
        else:
            return "general"
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        import re
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common LLM artifacts
        text = re.sub(r'^Based on the context[:\s]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^According to the document[:\s]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^The document states[:\s]*', '', text, flags=re.IGNORECASE)
        
        # Ensure proper capitalization
        if text and not text[0].isupper():
            text = text[0].upper() + text[1:]
        
        return text
    
    def apply_length_constraints(self, text: str, response_type: str) -> str:
        """Apply length constraints to the answer"""
        max_length = self.response_templates[response_type]["max_length"]
        
        if len(text) <= max_length:
            return text
        
        # Truncate at sentence boundary
        import re
        sentences = re.split(r'[.!?]+', text)
        truncated = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Add proper punctuation
            if not sentence[-1] in '.!?':
                sentence += '.'
            
            if len(truncated + sentence) <= max_length:
                truncated += sentence + " "
            else:
                break
        
        return truncated.strip()
    
    def format_response(self, answer: str, sources: List[Dict[str, Any]], confidence: float, query: str, threshold_used: float) -> Dict[str, Any]:
        """Format a complete response with proper structure and threshold handling"""
        
        # Determine response type
        response_type = self.classify_response_type(query)
        
        # Clean and format the answer
        cleaned_answer = self.clean_text(answer)
        
        # Apply template
        template = self.response_templates[response_type]["template"]
        formatted = template.format(answer=cleaned_answer)
        
        # Apply length constraints
        formatted = self.apply_length_constraints(formatted, response_type)
        
        # Format sources with threshold information
        formatted_sources = []
        for source in sources:
            formatted_source = {
                "doc_id": source.get("doc_id", ""),
                "doc_title": source.get("doc_title", ""),
                "section_title": source.get("section_title", ""),
                "similarity_score": round(source.get("similarity_score", 0), 4),
                "threshold_used": round(threshold_used, 4),
                "retrieval_method": source.get("retrieval_method", "semantic_search"),
                "page_number": source.get("page_number", -1),
                "chunk_id": source.get("chunk_id", ""),
                "text_preview": self.truncate_text(source.get("text", ""), 150)
            }
            formatted_sources.append(formatted_source)
        
        # Create response structure
        response = {
            "answer": formatted,
            "response_type": response_type,
            "confidence": round(confidence, 3),
            "total_sources": len(formatted_sources),
            "threshold_used": threshold_used,
            "query_processed": query,
            "sources": formatted_sources
        }
        
        # Add warnings if confidence is low
        warnings = self.generate_warnings(confidence, threshold_used, len(sources))
        if warnings:
            response["warnings"] = warnings
        
        return response
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        
        # Truncate at word boundary
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # If we can find a space in the last 20%
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def generate_warnings(self, confidence: float, threshold: float, source_count: int) -> List[str]:
        """Generate warnings based on response quality"""
        warnings = []
        
        if confidence < 0.5:
            warnings.append("Low confidence response - consider rephrasing your question")
        
        if threshold < 0.3:
            warnings.append("Using low similarity threshold - results may be less relevant")
        
        if source_count == 0:
            warnings.append("No relevant documents found - answer may be incomplete")
        elif source_count == 1:
            warnings.append("Limited source material - consider checking additional documents")
        
        return warnings
    
    def format_no_results_response(self, query: str, threshold: float) -> Dict[str, Any]:
        """Format responses when no results are found"""
        return {
            "answer": "I couldn't find specific information about this in the available policy documents. Please try rephrasing your question or check if the relevant documents have been uploaded.",
            "response_type": "no_results",
            "confidence": 0.0,
            "total_sources": 0,
            "threshold_used": threshold,
            "query_processed": query,
            "sources": [],
            "warnings": [
                "No relevant documents found",
                "Consider uploading additional policy documents",
                "Try using different keywords in your question"
            ]
        }

def demonstrate_improvements():
    """Demonstrate the response formatting improvements"""
    
    print("=== Response Formatting and Threshold Handling Improvements ===\n")
    
    # Initialize the demo formatter
    formatter = DemoResponseFormatter()
    
    # Test case 1: Your original waiting period query
    print("1. ORIGINAL QUERY: 'what is waiting period for this policy'")
    print("-" * 60)
    
    # Simulate the results from your example
    test_sources = [
        {
            "doc_id": "Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1_20250801_172833_646c7d83.pdf_20250801_115833",
            "doc_title": "National Insurance Company Limited",
            "section_title": "",
            "similarity_score": 0.0600295253,
            "structural_rank": 3,
            "threshold_used": 0.0600295253,
            "text": "hospitalisation treatment 9.1. Notification of Claim Notice with full particulars shall be sent to the Company/ TPA (if applicable) as under: i. Within 24hours from the date of emergency hospitalization required or before the Insured Person's discharge from Hospital, whichever is earlier. ii. At least 48 hours prior to admission in Hospital in case of a planned Hospitalization. 9.2. Documents to be submitted The reimbursement claim is to be supported with the following documents and submitted within the prescribed time limit. i. Duly completed claim form ii. Photo Identity proof of the patient iii. Medical practitioner's prescription advising admission. iv. Original bills with itemized break-up v. Payment receipts vi. Discharge summary including complete medical history of the patient along with other details. vii. Investigation/ Diagnostic test reports etc. supported by the prescription from attending medical practitioner viii. OT notes or Surgeon's certificate giving details of the operation performed (for surgical cases). ix. Sticker/Invoice of the Implants, wherever applicable. x. MLR (Medico Legal Report copy if carried out and FIR (First information report) if registered, where ever applicable. xi. NEFT Details (to enable direct credit of claim amount in bank account) and cancelled cheque xii. KYC (Identity proof with Address) of the proposer, where claim liability is above Rs. 1 Lakh as per AML Guidelines xiii. Legal heir/succession certificate, wherever applicable xiv. Any other relevant document required by Company/TPA for assessment of the claim.",
            "word_count": 1000,
            "legal_density": 0.004,
            "page_number": -1,
            "chunk_id": "section_0_chunk_8",
            "retrieval_method": "semantic_search"
        }
    ]
    
    test_answer = "Based on the policy document, there is no specific waiting period mentioned in the provided section. The document discusses claim notification procedures and required documents for hospitalization treatment, but does not contain information about waiting periods for coverage to begin."
    
    formatted_response = formatter.format_response(
        answer=test_answer,
        sources=test_sources,
        confidence=0.06,
        query="what is waiting period for this policy",
        threshold_used=0.06
    )
    
    print("IMPROVED RESPONSE:")
    print(json.dumps(formatted_response, indent=2))
    print(f"\nAnswer length: {len(formatted_response['answer'])} characters")
    print(f"Response type: {formatted_response['response_type']}")
    print(f"Confidence: {formatted_response['confidence']}")
    print(f"Warnings: {formatted_response.get('warnings', [])}")
    
    print("\n" + "="*80 + "\n")
    
    # Test case 2: High confidence procedural query
    print("2. HIGH CONFIDENCE QUERY: 'what documents are required for claim submission'")
    print("-" * 60)
    
    test_answer_2 = "According to the policy procedures, the following documents are required for claim submission: duly completed claim form, photo identity proof of the patient, medical practitioner's prescription advising admission, original bills with itemized break-up, payment receipts, discharge summary including complete medical history, investigation/diagnostic test reports, OT notes or surgeon's certificate for surgical cases, sticker/invoice of implants where applicable, MLR copy and FIR if applicable, NEFT details and cancelled cheque, KYC documents for claims above Rs. 1 Lakh, and legal heir/succession certificate where applicable."
    
    formatted_response_2 = formatter.format_response(
        answer=test_answer_2,
        sources=test_sources,
        confidence=0.85,
        query="what documents are required for claim submission",
        threshold_used=0.75
    )
    
    print("IMPROVED RESPONSE:")
    print(json.dumps(formatted_response_2, indent=2))
    print(f"\nAnswer length: {len(formatted_response_2['answer'])} characters")
    print(f"Response type: {formatted_response_2['response_type']}")
    print(f"Confidence: {formatted_response_2['confidence']}")
    print(f"Warnings: {formatted_response_2.get('warnings', [])}")
    
    print("\n" + "="*80 + "\n")
    
    # Test case 3: No results scenario
    print("3. NO RESULTS SCENARIO: 'what is the premium amount for this policy'")
    print("-" * 60)
    
    no_results_response = formatter.format_no_results_response(
        query="what is the premium amount for this policy",
        threshold=0.7
    )
    
    print("IMPROVED RESPONSE:")
    print(json.dumps(no_results_response, indent=2))
    
    print("\n" + "="*80 + "\n")
    
    # Summary of improvements
    print("SUMMARY OF IMPROVEMENTS:")
    print("-" * 60)
    print("✅ Structured response format with consistent fields")
    print("✅ Automatic response type classification")
    print("✅ Length control based on response type")
    print("✅ Enhanced threshold handling with detailed information")
    print("✅ Intelligent warning system based on confidence and threshold")
    print("✅ Text cleaning and normalization")
    print("✅ Professional formatting with proper templates")
    print("✅ Comprehensive source information with previews")
    print("✅ Error handling and edge case management")
    print("✅ Configurable response parameters")

if __name__ == "__main__":
    demonstrate_improvements() 