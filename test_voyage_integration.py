#!/usr/bin/env python3
"""
Test script to verify Voyage AI integration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_voyage_configuration():
    """Test Voyage AI configuration"""
    print("Testing Voyage AI Configuration...")
    
    # Check if VOYAGE_API_KEY is set
    voyage_api_key = os.getenv("VOYAGE_API_KEY")
    if not voyage_api_key:
        print("❌ VOYAGE_API_KEY not found in environment")
        return False
    
    print("✅ VOYAGE_API_KEY found")
    return True

def test_voyage_import():
    """Test Voyage AI import"""
    print("Testing Voyage AI Import...")
    
    try:
        from voyageai import Client
        print("✅ Voyage AI client imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Voyage AI client: {e}")
        print("Please install voyageai: pip install voyageai")
        return False

def test_voyage_client():
    """Test Voyage AI client initialization"""
    print("Testing Voyage AI Client...")
    
    try:
        from voyageai import Client
        from config.settings import settings
        
        client = Client(api_key=settings.VOYAGE_API_KEY)
        print("✅ Voyage AI client initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Voyage AI client: {e}")
        return False

def test_embedding_client():
    """Test embedding client"""
    print("Testing Embedding Client...")
    
    try:
        from embeddings.embed_client import EmbeddingClient
        
        client = EmbeddingClient()
        print("✅ Embedding client initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize embedding client: {e}")
        return False

def test_llm_client():
    """Test LLM client"""
    print("Testing LLM Client...")
    
    try:
        from llm_service.llm_client import LLMClient
        
        client = LLMClient()
        print("✅ LLM client initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize LLM client: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("VOYAGE AI INTEGRATION TEST")
    print("=" * 60)
    print()
    
    tests = [
        test_voyage_configuration,
        test_voyage_import,
        test_voyage_client,
        test_embedding_client,
        test_llm_client
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
        print("✅ All Voyage AI integration tests passed!")
        print("Your system is ready to use Voyage AI.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("Make sure to:")
        print("1. Install voyageai: pip install voyageai")
        print("2. Set VOYAGE_API_KEY in your .env file")
        print("3. Check your Voyage AI API key and billing")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 