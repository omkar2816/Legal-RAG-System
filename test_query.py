#!/usr/bin/env python3
"""
Test script to query the uploaded document
"""
import requests

def test_query():
    """Test querying the uploaded document"""
    print("Testing document query...")
    
    try:
        # Test questions about the NDA document
        questions = [
            "What is the purpose of this agreement?",
            "What are the confidentiality obligations?",
            "What is the term of this agreement?",
            "What happens if there is a breach?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n--- Question {i}: {question} ---")
            
            response = requests.post(
                f'http://localhost:8000/query/ask?question={question}',
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("✅ Query successful!")
                print(f"Answer: {result.get('answer', 'No answer provided')}")
                print(f"Sources: {result.get('sources', [])}")
            else:
                print(f"❌ Query failed: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_query() 