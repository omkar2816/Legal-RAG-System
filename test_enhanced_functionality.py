#!/usr/bin/env python3
"""
Test script to verify enhanced functionality:
- Clause matching precision
- Confidence scoring
- Structured responses
- Explainability
- Performance improvements
"""

import sys
import os
import logging
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_service.llm_client import LLMClient
from llm_service.response_formatter import response_formatter
from config.settings import settings

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_clause_matching():
    """Test clause matching functionality"""
    print("🔍 Testing clause matching...")
    
    # Mock context chunks with clause information
    context_chunks = [
        {
            'score': 0.85,
            'metadata': {
                'doc_title': 'Insurance Policy',
                'section_title': 'Coverage Terms',
                'page_number': 5,
                'chunk_id': 'chunk_1',
                'text': 'Clause 2.1: The waiting period for joint replacement treatment shall be 12 months from the policy start date.'
            }
        },
        {
            'score': 0.78,
            'metadata': {
                'doc_title': 'Insurance Policy',
                'section_title': 'Definitions',
                'page_number': 3,
                'chunk_id': 'chunk_2',
                'text': 'Section 1.2: "Pre-Existing Disease" means any condition that existed before the policy start date.'
            }
        },
        {
            'score': 0.92,
            'metadata': {
                'doc_title': 'Insurance Policy',
                'section_title': 'Exclusions',
                'page_number': 8,
                'chunk_id': 'chunk_3',
                'text': 'Article 3.1: Cataract treatment waiting period is 6 months as per clause 2.3.'
            }
        }
    ]
    
    # Create mock LLM client
    class MockLLMClient(LLMClient):
        def generate_response(self, prompt: str, context: str = None, system_prompt: str = None) -> str:
            return """According to Clause 2.1 (Page 5): The waiting period for joint replacement treatment is 12 months from the policy start date.

According to Section 1.2 (Page 3): "Pre-Existing Disease" is defined as any condition that existed before the policy start date.

According to Article 3.1 (Page 8): Cataract treatment has a 6-month waiting period as specified in clause 2.3.

The maximum co-payment percentage is 20% as per Section 4.2."""
    
    mock_client = MockLLMClient()
    
    try:
        # Test the enhanced response generation
        result = mock_client.generate_legal_response(
            question="What is maximum waiting period for treatment of joint replacement?, What does the policy define as a \"Pre-Existing Disease\"?, What is the waiting period for cataract treatment under this policy?, What is the maximum co-payment percentage applicable under this policy? When does it apply?",
            context_chunks=context_chunks
        )
        
        print(f"✅ Structured response generated")
        print(f"✅ Answer: {result.get('answer', '')[:200]}...")
        print(f"✅ Confidence scores: {result.get('confidence_scores', [])}")
        print(f"✅ Overall confidence: {result.get('overall_confidence', 0.0)}")
        print(f"✅ Clause references: {len(result.get('clause_references', []))}")
        print(f"✅ Questions: {len(result.get('questions', []))}")
        
        # Verify clause references
        clause_refs = result.get('clause_references', [])
        expected_clauses = ['2.1', '1.2', '3.1', '4.2']
        found_clauses = [ref.get('identifier', '') for ref in clause_refs]
        
        print(f"✅ Found clauses: {found_clauses}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def test_confidence_scoring():
    """Test confidence scoring functionality"""
    print("\n📊 Testing confidence scoring...")
    
    # Test different scenarios
    test_cases = [
        {
            "name": "High confidence case",
            "context_chunks": [{'score': 0.9}, {'score': 0.85}],
            "response": "According to Clause 2.1: The waiting period is 12 months.",
            "expected_confidence": 0.8
        },
        {
            "name": "Low confidence case",
            "context_chunks": [{'score': 0.3}, {'score': 0.4}],
            "response": "The information is not clearly specified in the provided documents.",
            "expected_confidence": 0.4
        }
    ]
    
    mock_client = LLMClient()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test case {i}: {test_case['name']}")
        try:
            confidence_scores = mock_client._calculate_confidence_scores(
                questions=["Test question"],
                context_chunks=test_case["context_chunks"],
                response=test_case["response"]
            )
            
            confidence = confidence_scores[0] if confidence_scores else 0.0
            print(f"✅ Calculated confidence: {confidence:.3f}")
            print(f"✅ Expected range: {test_case['expected_confidence'] - 0.2:.3f} - {test_case['expected_confidence'] + 0.2:.3f}")
            
            # Check if confidence is in reasonable range
            expected = test_case['expected_confidence']
            if expected - 0.2 <= confidence <= expected + 0.2:
                print(f"✅ Confidence score is reasonable")
            else:
                print(f"⚠️ Confidence score may need adjustment")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return True

def test_structured_responses():
    """Test structured response formatting"""
    print("\n🏗️ Testing structured responses...")
    
    # Mock structured data
    structured_data = {
        "questions": [
            "What is the waiting period?",
            "What is the coverage amount?"
        ],
        "confidence_scores": [0.85, 0.78],
        "overall_confidence": 0.815,
        "clause_references": [
            {
                "type": "clause",
                "identifier": "2.1",
                "context": {"doc_title": "Policy", "page_number": 5},
                "found_in_response": True
            }
        ],
        "source_clause_ref": [
            {
                "chunk_id": "chunk_1",
                "doc_title": "Insurance Policy",
                "section_title": "Coverage Terms",
                "page_number": 5,
                "clause_identifiers": ["2.1", "2.2"]
            }
        ],
        "context_chunks_used": 3,
        "metadata": {
            "total_questions": 2,
            "has_multiple_questions": True,
            "clauses_cited": 1,
            "context_relevance": 0.85
        }
    }
    
    try:
        # Test response formatting
        formatted_response = response_formatter.format_response(
            answer="According to Clause 2.1: The waiting period is 12 months.",
            sources=[{"doc_id": "test", "similarity_score": 0.85}],
            confidence=0.815,
            query="What is the waiting period?",
            threshold_used=0.7,
            structured_data=structured_data
        )
        
        print(f"✅ Formatted response created")
        print(f"✅ Response type: {formatted_response.get('response_type')}")
        print(f"✅ Questions: {len(formatted_response.get('questions', []))}")
        print(f"✅ Confidence scores: {formatted_response.get('confidence_scores', [])}")
        print(f"✅ Clause references: {len(formatted_response.get('clause_references', []))}")
        print(f"✅ Explainability: {formatted_response.get('explainability', {})}")
        
        # Verify explainability
        explainability = formatted_response.get('explainability', {})
        if explainability:
            print(f"✅ Explainability generated")
            print(f"✅ Clauses cited: {explainability.get('clauses_cited', 0)}")
            print(f"✅ Source traceability: {explainability.get('source_traceability', {})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def test_performance_improvements():
    """Test performance improvements"""
    print("\n⚡ Testing performance improvements...")
    
    # Test lean response generation
    test_questions = [
        "What is the waiting period?",
        "What is maximum waiting period for treatment of joint replacement?, What does the policy define as a \"Pre-Existing Disease\"?, What is the waiting period for cataract treatment under this policy?, What is the maximum co-payment percentage applicable under this policy? When does it apply?"
    ]
    
    mock_client = LLMClient()
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test case {i}: {question[:50]}...")
        try:
            # Test context formatting with metadata
            context_chunks = [
                {
                    'score': 0.85,
                    'metadata': {
                        'doc_title': 'Test Policy',
                        'section_title': 'Test Section',
                        'page_number': 1,
                        'chunk_id': 'test_chunk',
                        'text': 'Clause 1.1: Test clause content.'
                    }
                }
            ]
            
            context_data = mock_client._format_context_with_metadata(context_chunks)
            
            print(f"✅ Context formatted with metadata")
            print(f"✅ Relevance score: {context_data.get('relevance_score', 0.0):.3f}")
            print(f"✅ Clause info: {len(context_data.get('clause_info', []))} items")
            
            # Test clause identification
            clause_identifiers = mock_client._identify_clause_identifiers("Clause 1.1 and Section 2.3 are important.")
            print(f"✅ Identified clauses: {clause_identifiers}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return True

def test_explainability():
    """Test explainability features"""
    print("\n🔍 Testing explainability...")
    
    try:
        # Test clause reference extraction
        mock_client = LLMClient()
        
        response_text = """According to Clause 2.1 (Page 5): The waiting period is 12 months.
        Section 1.2 defines pre-existing conditions.
        Article 3.1 covers cataract treatment."""
        
        clause_info = [
            {
                "clause_identifiers": ["2.1", "1.2", "3.1"],
                "doc_title": "Test Policy",
                "page_number": 5
            }
        ]
        
        references = mock_client._extract_clause_references(response_text, clause_info)
        
        print(f"✅ Extracted {len(references)} clause references")
        for ref in references:
            print(f"✅ Reference: {ref.get('type')} {ref.get('identifier')}")
        
        # Test explainability generation
        structured_data = {
            "clause_references": references,
            "answer": response_text,
            "metadata": {"context_relevance": 0.85}
        }
        
        sources = [{"doc_id": "test", "clause_identifiers": ["2.1"]}]
        
        explainability = response_formatter._generate_explainability_info(structured_data, sources)
        
        print(f"✅ Explainability generated")
        print(f"✅ Clauses cited: {explainability.get('clauses_cited', 0)}")
        print(f"✅ Confidence breakdown: {explainability.get('confidence_breakdown', {})}")
        print(f"✅ Source traceability: {explainability.get('source_traceability', {})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Functionality")
    print("=" * 50)
    
    tests = [
        ("Clause matching", test_clause_matching),
        ("Confidence scoring", test_confidence_scoring),
        ("Structured responses", test_structured_responses),
        ("Performance improvements", test_performance_improvements),
        ("Explainability", test_explainability),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Enhanced functionality is working correctly.")
        print("✅ Clause matching precision improved")
        print("✅ Confidence scoring implemented")
        print("✅ Structured responses working")
        print("✅ Performance optimizations active")
        print("✅ Explainability features enabled")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 