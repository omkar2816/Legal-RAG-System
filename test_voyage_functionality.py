#!/usr/bin/env python3
"""
Test script to verify Voyage AI functionality with actual API calls
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_embedding_generation():
    """Test embedding generation with Voyage AI"""
    print("Testing Embedding Generation...")
    
    try:
        from embeddings.embed_client import EmbeddingClient
        
        client = EmbeddingClient()
        
        # Test texts
        test_texts = [
            "What is the employee's base salary?",
            "What are the termination provisions?",
            "What is the non-competition period?"
        ]
        
        print(f"Generating embeddings for {len(test_texts)} texts...")
        embeddings = client.get_embeddings(test_texts)
        
        if embeddings and len(embeddings) == len(test_texts):
            print(f"✅ Successfully generated {len(embeddings)} embeddings")
            print(f"   Embedding dimension: {len(embeddings[0])}")
            return True
        else:
            print("❌ Failed to generate embeddings")
            return False
            
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return False

def test_llm_response():
    """Test LLM response generation with Voyage AI"""
    print("Testing LLM Response Generation...")
    
    try:
        from llm_service.llm_client import LLMClient
        
        client = LLMClient()
        
        # Test prompt
        test_prompt = "What is the capital of France?"
        
        print(f"Generating response for: '{test_prompt}'")
        response = client.generate_response(test_prompt)
        
        if response and len(response) > 0:
            print(f"✅ Successfully generated response: {response[:100]}...")
            return True
        else:
            print("❌ Failed to generate response")
            return False
            
    except Exception as e:
        print(f"❌ LLM response generation failed: {e}")
        return False

def test_legal_response():
    """Test legal-specific response generation"""
    print("Testing Legal Response Generation...")
    
    try:
        from llm_service.llm_client import LLMClient
        
        client = LLMClient()
        
        # Test legal context and question
        context = "The Company shall pay the Employee an annual base salary of $120,000, payable in accordance with the Company's normal payroll practices."
        question = "What is the employee's base salary?"
        
        print(f"Generating legal response for: '{question}'")
        response = client.generate_legal_response(question, [{"text": context, "metadata": {}}])
        
        if response and len(response) > 0:
            print(f"✅ Successfully generated legal response: {response[:100]}...")
            return True
        else:
            print("❌ Failed to generate legal response")
            return False
            
    except Exception as e:
        print(f"❌ Legal response generation failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("VOYAGE AI FUNCTIONALITY TEST")
    print("=" * 60)
    print()
    
    # Check if API key is available
    voyage_api_key = os.getenv("VOYAGE_API_KEY")
    if not voyage_api_key:
        print("❌ VOYAGE_API_KEY not found in environment")
        print("Please set your Voyage AI API key in the .env file")
        return
    
    tests = [
        test_embedding_generation,
        test_llm_response,
        test_legal_response
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All Voyage AI functionality tests passed!")
        print("Your system is fully functional with Voyage AI.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("Make sure to:")
        print("1. Check your Voyage AI API key and billing")
        print("2. Verify your internet connection")
        print("3. Check the Voyage AI service status")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 