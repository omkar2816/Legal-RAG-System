#!/usr/bin/env python3
"""
Test script to verify the multiple questions fix
Tests that the system can handle multiple questions without throwing "'bool' object is not iterable" error
"""

import sys
import os
import logging
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.query_enhancer import detect_multiple_questions, query_enhancer
from llm_service.llm_client import LLMClient

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_detect_multiple_questions():
    """Test the detect_multiple_questions function with various inputs"""
    print("🔍 Testing detect_multiple_questions function...")
    
    test_cases = [
        # Normal multiple questions
        "What is maximum waiting period for treatment of joint replacement?, What does the policy define as a \"Pre-Existing Disease\"?, What is the waiting period for cataract treatment under this policy?, What is the maximum co-payment percentage applicable under this policy? When does it apply?",
        
        # Single question
        "What is the coverage limit for hospitalization?",
        
        # Questions with different separators
        "What are the exclusions? What is the claim process?",
        "What is the waiting period; What is the coverage amount?",
        "What is covered and what is not covered?",
        
        # Edge cases
        "",  # Empty string
        None,  # None value
        123,  # Integer
        True,  # Boolean
        False,  # Boolean
        ["test"],  # List
        {"test": "value"},  # Dict
        
        # Complex multiple questions
        "What is the maximum waiting period for treatment of joint replacement? What does the policy define as a \"Pre-Existing Disease\"? What is the waiting period for cataract treatment under this policy? What is the maximum co-payment percentage applicable under this policy? When does it apply?"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test case {i}: {repr(test_case)}")
        try:
            result = detect_multiple_questions(test_case)
            print(f"✅ Result type: {type(result)}")
            print(f"✅ Result: {result}")
            print(f"✅ Length: {len(result)}")
            
            # Verify result is always a list
            assert isinstance(result, list), f"Expected list, got {type(result)}"
            
            # Verify all items are strings
            for j, item in enumerate(result):
                assert isinstance(item, str), f"Expected string at index {j}, got {type(item)}"
            
            print(f"✅ Validation passed")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    print("\n🎉 All detect_multiple_questions tests passed!")
    return True

def test_llm_client_multiple_questions():
    """Test the LLM client with multiple questions"""
    print("\n🤖 Testing LLM client with multiple questions...")
    
    # Create a mock LLM client for testing
    class MockLLMClient(LLMClient):
        def generate_response(self, prompt: str, context: str = None, system_prompt: str = None) -> str:
            return "This is a mock response for testing purposes."
        
        def _format_context(self, context_chunks: List[Dict[str, Any]]) -> str:
            return "Mock context for testing"
    
    # Test cases
    test_questions = [
        "What is maximum waiting period for treatment of joint replacement?, What does the policy define as a \"Pre-Existing Disease\"?",
        "What is the coverage limit?",
        "What are the exclusions and what is the claim process?",
        "",  # Empty
        None,  # None
        123,  # Integer
        True,  # Boolean
    ]
    
    mock_client = MockLLMClient()
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Testing LLM client with question {i}: {repr(question)}")
        try:
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
            
            result = mock_client.generate_legal_response(question, context_chunks)
            print(f"✅ Result: {result}")
            print(f"✅ No errors occurred")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    print("\n🎉 All LLM client tests passed!")
    return True

def test_edge_cases():
    """Test edge cases that might cause the boolean error"""
    print("\n🔬 Testing edge cases...")
    
    edge_cases = [
        # Boolean values
        True,
        False,
        
        # Numeric values
        0,
        1,
        3.14,
        
        # Complex types
        [],
        {},
        set(),
        tuple(),
        
        # None values
        None,
        
        # Mixed types in list (if somehow passed)
        [True, False, "test", 123],
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

def test_class_method():
    """Test the class method directly"""
    print("\n🏗️ Testing LegalQueryEnhancer.detect_multiple_questions method...")
    
    test_cases = [
        "What is the coverage? What is the exclusion?",
        True,
        False,
        None,
        123,
        "",
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test case {i}: {repr(test_case)}")
        try:
            result = query_enhancer.detect_multiple_questions(test_case)
            print(f"✅ Result: {result}")
            print(f"✅ Type: {type(result)}")
            
            # Verify result is always a list
            assert isinstance(result, list), f"Expected list, got {type(result)}"
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    print("\n🎉 All class method tests passed!")
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Multiple Questions Fix Tests")
    print("=" * 50)
    
    tests = [
        ("detect_multiple_questions function", test_detect_multiple_questions),
        ("LLM client multiple questions", test_llm_client_multiple_questions),
        ("Edge cases", test_edge_cases),
        ("Class method", test_class_method),
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
        print("🎉 ALL TESTS PASSED! The multiple questions fix is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 