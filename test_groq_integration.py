#!/usr/bin/env python3
"""
Test script for Groq integration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_service.llm_client import LLMClient, call_llm

def test_groq_integration():
    """Test Groq integration"""
    print("Testing Groq Integration...")
    
    # Check if Groq API key is set
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Please set your Groq API key in the .env file")
        return False
    
    try:
        # Test basic LLM client
        print("1. Testing LLM Client initialization...")
        client = LLMClient()
        print("✅ LLM Client initialized successfully")
        
        # Test simple response generation
        print("2. Testing simple response generation...")
        response = client.generate_response("Hello, how are you?")
        print(f"✅ Response generated: {response[:100]}...")
        
        # Test with system prompt
        print("3. Testing with system prompt...")
        system_prompt = "You are a helpful legal assistant."
        response = client.generate_response(
            "What is a contract?",
            system_prompt=system_prompt
        )
        print(f"✅ Response with system prompt: {response[:100]}...")
        
        # Test convenience function
        print("4. Testing convenience function...")
        response = call_llm("Explain what is a legal document.")
        print(f"✅ Convenience function response: {response[:100]}...")
        
        print("\n🎉 All Groq integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_groq_integration()
    sys.exit(0 if success else 1) 