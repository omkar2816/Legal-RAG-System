#!/usr/bin/env python3
"""
Test script for improved response formatting and threshold handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_service.response_formatter import response_formatter, ResponseConfig
from vectordb.advanced_retrieval import retrieve_documents_advanced
import json

def test_response_formatting():
    """Test the response formatter with different scenarios"""
    
    print("=== Testing Response Formatting ===\n")
    
    # Test case 1: Waiting period query (from your example)
    print("1. Testing waiting period query:")
    test_query = "what is waiting period for this policy"
    
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
    
    formatted_response = response_formatter.format_response(
        answer=test_answer,
        sources=test_sources,
        confidence=0.06,
        query=test_query,
        threshold_used=0.06
    )
    
    print(f"Query: {test_query}")
    print(f"Formatted Response:")
    print(json.dumps(formatted_response, indent=2))
    print("\n" + "="*80 + "\n")
    
    # Test case 2: High confidence response
    print("2. Testing high confidence response:")
    test_query_2 = "what documents are required for claim submission"
    test_answer_2 = "According to the policy procedures, the following documents are required for claim submission: duly completed claim form, photo identity proof of the patient, medical practitioner's prescription advising admission, original bills with itemized break-up, payment receipts, discharge summary including complete medical history, investigation/diagnostic test reports, OT notes or surgeon's certificate for surgical cases, sticker/invoice of implants where applicable, MLR copy and FIR if applicable, NEFT details and cancelled cheque, KYC documents for claims above Rs. 1 Lakh, and legal heir/succession certificate where applicable."
    
    formatted_response_2 = response_formatter.format_response(
        answer=test_answer_2,
        sources=test_sources,
        confidence=0.85,
        query=test_query_2,
        threshold_used=0.75
    )
    
    print(f"Query: {test_query_2}")
    print(f"Formatted Response:")
    print(json.dumps(formatted_response_2, indent=2))
    print("\n" + "="*80 + "\n")
    
    # Test case 3: No results scenario
    print("3. Testing no results scenario:")
    no_results_response = response_formatter.format_no_results_response(
        query="what is the premium amount for this policy",
        threshold=0.7
    )
    
    print("Query: what is the premium amount for this policy")
    print("No Results Response:")
    print(json.dumps(no_results_response, indent=2))
    print("\n" + "="*80 + "\n")
    
    # Test case 4: Error scenario
    print("4. Testing error scenario:")
    error_response = response_formatter.format_error_response(
        error="Database connection failed",
        query="what is covered under this policy"
    )
    
    print("Query: what is covered under this policy")
    print("Error Response:")
    print(json.dumps(error_response, indent=2))
    print("\n" + "="*80 + "\n")

def test_threshold_handling():
    """Test the enhanced threshold handling"""
    
    print("=== Testing Threshold Handling ===\n")
    
    # Test different threshold scenarios
    test_queries = [
        "what is waiting period for this policy",
        "what documents are required for claims",
        "what is covered under this policy",
        "how to submit a claim"
    ]
    
    for query in test_queries:
        print(f"Testing query: {query}")
        try:
            # Test with different threshold values
            for threshold in [0.3, 0.5, 0.7]:
                print(f"  Threshold: {threshold}")
                results = retrieve_documents_advanced(
                    query=query,
                    top_k=3,
                    threshold=threshold,
                    return_count=3,
                    adaptive_threshold=True
                )
                
                if results:
                    print(f"    Results found: {len(results)}")
                    print(f"    Best score: {results[0].get('similarity_score', 0):.4f}")
                    print(f"    Threshold used: {results[0].get('threshold_used', threshold):.4f}")
                else:
                    print(f"    No results found")
                print()
        except Exception as e:
            print(f"    Error: {e}")
        
        print("-" * 60)

def test_custom_config():
    """Test custom response configuration"""
    
    print("=== Testing Custom Configuration ===\n")
    
    # Create custom configuration
    custom_config = ResponseConfig(
        max_length=200,
        min_length=30,
        include_sources=True,
        include_confidence=True,
        include_threshold_info=True,
        format_type="compact"
    )
    
    custom_formatter = response_formatter.__class__(custom_config)
    
    test_query = "what is waiting period for this policy"
    test_answer = "Based on the policy document, there is no specific waiting period mentioned in the provided section. The document discusses claim notification procedures and required documents for hospitalization treatment, but does not contain information about waiting periods for coverage to begin."
    
    test_sources = [
        {
            "doc_id": "test_doc_1",
            "doc_title": "Test Policy",
            "similarity_score": 0.06,
            "text": "Sample text for testing"
        }
    ]
    
    formatted_response = custom_formatter.format_response(
        answer=test_answer,
        sources=test_sources,
        confidence=0.06,
        query=test_query,
        threshold_used=0.06
    )
    
    print(f"Custom Configuration Response:")
    print(json.dumps(formatted_response, indent=2))
    print(f"Answer length: {len(formatted_response['answer'])} characters")

if __name__ == "__main__":
    print("Testing Improved Response Formatting and Threshold Handling\n")
    print("=" * 80)
    
    try:
        test_response_formatting()
        test_threshold_handling()
        test_custom_config()
        
        print("\n=== All Tests Completed Successfully ===")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc() 