#!/usr/bin/env python3
"""
Test script to verify the specific error fix for "'bool' object is not iterable"
"""

import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.query_enhancer import detect_multiple_questions
from llm_service.llm_client import LLMClient

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_specific_error_case():
    """Test the specific error case mentioned by the user"""
    print("🔍 Testing the specific error case...")
    
    # The exact query that caused the error
    problematic_query = "What is maximum waiting period for treatment of joint replacement?, What does the policy define as a \"Pre-Existing Disease\"?, What is the waiting period for cataract treatment under this policy?, What is the maximum co-payment percentage applicable under this policy? When does it apply?"
    
    print(f"📝 Testing query: {problematic_query}")
    
    try:
        # Test the detect_multiple_questions function
        print("🔍 Testing detect_multiple_questions function...")
        result = detect_multiple_questions(problematic_query)
        print(f"✅ detect_multiple_questions result: {result}")
        print(f"✅ Type: {type(result)}")
        print(f"✅ Length: {len(result)}")
        
        # Verify it's a list
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        
        # Test with LLM client (mock)
        print("🔍 Testing LLM client...")
        class MockLLMClient(LLMClient):
            def generate_response(self, prompt: str, context: str = None, system_prompt: str = None) -> str:
                return "This is a mock response for testing the fix."
            
            def _format_context(self, context_chunks):
                return "Mock context"
        
        mock_client = MockLLMClient()
        
        # Mock context chunks
        context_chunks = [
            {
                'score': 0.8,
                'metadata': {
                    'text': 'Sample policy text for testing',
                    'doc_id': 'test_doc',
                    'doc_title': 'Test Policy'
                }
            }
        ]
        
        # Test the generate_legal_response method
        response = mock_client.generate_legal_response(problematic_query, context_chunks)
        print(f"✅ LLM client response: {response}")
        print(f"✅ No errors occurred!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

def test_edge_cases():
    """Test various edge cases that might cause the boolean error"""
    print("\n🔬 Testing edge cases...")
    
    edge_cases = [
        True,
        False,
        None,
        "",
        123,
        ["test"],
        {"test": "value"},
    ]
    
    for i, edge_case in enumerate(edge_cases, 1):
        print(f"\n📝 Edge case {i}: {repr(edge_case)} (type: {type(edge_case)})")
        try:
            result = detect_multiple_questions(edge_case)
            print(f"✅ Result: {result}")
            print(f"✅ Type: {type(result)}")
            
            # Verify result is always a list
            assert isinstance(result, list), f"Expected list, got {type(result)}"
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    print("\n🎉 All edge case tests passed!")
    return True

def test_multiple_questions():
    """Test various multiple question formats"""
    print("\n🔍 Testing multiple question formats...")
    
    test_cases = [
        "What is the coverage? What is the exclusion?",
        "What is the waiting period, What is the coverage amount?",
        "What is covered and what is not covered?",
        "What is the policy? What are the terms? What is the process?",
        "What is maximum waiting period for treatment of joint replacement?, What does the policy define as a \"Pre-Existing Disease\"?, What is the waiting period for cataract treatment under this policy?, What is the maximum co-payment percentage applicable under this policy? When does it apply?"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test case {i}: {repr(test_case)}")
        try:
            result = detect_multiple_questions(test_case)
            print(f"✅ Result: {result}")
            print(f"✅ Type: {type(result)}")
            print(f"✅ Length: {len(result)}")
            
            # Verify result is always a list
            assert isinstance(result, list), f"Expected list, got {type(result)}"
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    print("\n🎉 All multiple questions tests passed!")
    return True

def main():
    """Run the tests"""
    print("🚀 Testing Specific Error Fix")
    print("=" * 50)
    
    tests = [
        ("Specific error case", test_specific_error_case),
        ("Edge cases", test_edge_cases),
        ("Multiple questions", test_multiple_questions),
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
        print("🎉 ALL TESTS PASSED! The error fix is working correctly.")
        print("✅ The 'bool' object is not iterable error should be resolved.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 