#!/usr/bin/env python3
"""
Test script for query normalization functionality
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.validation import ValidationUtils

def test_query_normalization():
    """Test the query normalization function with various test cases"""
    
    validation_utils = ValidationUtils()
    
    # Test cases
    test_cases = [
        {
            "input": "What are the pre-existing disease exclusions?",
            "expected": "what are the preexisting diseases exclusions?"
        },
        {
            "input": "How much is the PED coverage?",
            "expected": "how much is the preexisting diseases coverage?"
        },
        {
            "input": "What are the claim amount limits?",
            "expected": "what are the expenses limits?"
        },
        {
            "input": "Tell me about the insurance premium payment",
            "expected": "tell me about the premium payment"
        },
        {
            "input": "What is the deductible amount?",
            "expected": "what is the deductible?"
        },
        {
            "input": "How do I file an insurance claim?",
            "expected": "how do i file a claim?"
        },
        {
            "input": "What is the waiting time for coverage?",
            "expected": "what is the waiting period for coverage?"
        },
        {
            "input": "Can you explain the policy renewal process?",
            "expected": "can you explain the renewal process?"
        },
        {
            "input": "What happens during policy termination?",
            "expected": "what happens during termination?"
        },
        {
            "input": "What are the excluded conditions?",
            "expected": "what are the exclusion?"
        }
    ]
    
    print("🧪 Testing Query Normalization Function")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        input_query = test_case["input"]
        expected = test_case["expected"]
        
        # Test the normalize_query function directly
        result = validation_utils.normalize_query(input_query)
        
        # Test the validate_query function (which uses normalize_query)
        validation_result = validation_utils.validate_query(input_query)
        normalized_from_validation = validation_result["cleaned_query"]
        
        print(f"\nTest {i}:")
        print(f"  Input:     '{input_query}'")
        print(f"  Expected:   '{expected}'")
        print(f"  Result:     '{result}'")
        print(f"  Validation: '{normalized_from_validation}'")
        
        # Check if both results match expected
        if result == expected and normalized_from_validation == expected:
            print(f"  ✅ PASS")
            passed += 1
        else:
            print(f"  ❌ FAIL")
            print(f"    - Direct normalization: {'✅' if result == expected else '❌'}")
            print(f"    - Validation normalization: {'✅' if normalized_from_validation == expected else '❌'}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Query normalization is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return failed == 0

def test_edge_cases():
    """Test edge cases for the normalization function"""
    
    validation_utils = ValidationUtils()
    
    print("\n🔍 Testing Edge Cases")
    print("=" * 30)
    
    edge_cases = [
        ("", ""),  # Empty string
        ("   ", ""),  # Whitespace only
        ("HELLO WORLD", "hello world"),  # All caps
        ("Pre-Existing Disease", "preexisting diseases"),  # Mixed case
        ("PED and expenses", "preexisting diseases and expenses"),  # Multiple replacements
        ("No synonyms here", "no synonyms here"),  # No replacements needed
    ]
    
    for input_query, expected in edge_cases:
        result = validation_utils.normalize_query(input_query)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_query}' -> '{result}' (expected: '{expected}')")

if __name__ == "__main__":
    print("🚀 Legal RAG System - Query Normalization Test")
    print("=" * 60)
    
    # Run main tests
    success = test_query_normalization()
    
    # Run edge case tests
    test_edge_cases()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Query normalization integration completed successfully!")
        print("\n📝 Usage:")
        print("   The normalize_query function is now integrated into the ValidationUtils class.")
        print("   It will automatically be used when processing queries through the API endpoints.")
        print("   You can also use it directly: validation_utils.normalize_query('your query')")
    else:
        print("❌ Some tests failed. Please review the implementation.")
    
    sys.exit(0 if success else 1) 