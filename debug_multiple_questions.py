#!/usr/bin/env python3
"""
Debug script to test detect_multiple_questions function
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query_enhancer import detect_multiple_questions

def test_detect_multiple_questions():
    """Test the detect_multiple_questions function with various inputs"""
    
    test_cases = [
        "What are the pre-existing disease exclusions? What is the coverage limit for hospitalization?",
        "How do I file a claim? What is the waiting period?",
        "What is the deductible amount?",
        "What are the premium payment terms? What happens if I miss a payment?",
        "What is the termination process?",
        "",  # Empty string
        None,  # None value
        True,  # Boolean
        123,   # Number
    ]
    
    print("🔍 Testing detect_multiple_questions function")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {repr(test_case)}")
        try:
            result = detect_multiple_questions(test_case)
            print(f"Result type: {type(result)}")
            print(f"Result: {result}")
            
            # Check if result is iterable
            if hasattr(result, '__iter__') and not isinstance(result, str):
                print(f"✅ Result is iterable, length: {len(result)}")
            else:
                print(f"❌ Result is NOT iterable!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_detect_multiple_questions() 