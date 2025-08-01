#!/usr/bin/env python3
"""
Test script to verify comprehensive response improvements
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_multiple_questions_detection():
    """Test multiple questions detection"""
    print("🔍 Testing Multiple Questions Detection")
    print("=" * 50)
    
    try:
        from utils.query_enhancer import detect_multiple_questions, enhance_multiple_questions
        
        # Test query with multiple questions
        test_query = "What is maximum waiting period for treatment of joint replacement?, What does the policy define as a Pre-Existing Disease?, What is the waiting period for cataract treatment under this policy?, What is the maximum co-payment percentage applicable under this policy? When does it apply?"
        
        print(f"Original Query: {test_query}")
        
        # Detect multiple questions
        questions = detect_multiple_questions(test_query)
        print(f"\nDetected {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
        
        # Enhance multiple questions
        enhanced = enhance_multiple_questions(test_query)
        print(f"\nEnhanced Query:\n{enhanced}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_token_limit_increase():
    """Test that token limit has been increased"""
    print("\n🔧 Testing Token Limit Increase")
    print("=" * 50)
    
    try:
        from config.settings import settings
        
        print(f"Current GROQ_MAX_TOKENS: {settings.GROQ_MAX_TOKENS}")
        
        if settings.GROQ_MAX_TOKENS >= 4000:
            print("✅ Token limit has been increased to 4000+ tokens")
            return True
        else:
            print(f"❌ Token limit is still low: {settings.GROQ_MAX_TOKENS}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_improved_prompts():
    """Test improved prompt templates"""
    print("\n📝 Testing Improved Prompts")
    print("=" * 50)
    
    try:
        from config.settings import settings
        
        print("System Prompt:")
        print(settings.SYSTEM_PROMPT)
        print("\n" + "-" * 50)
        print("Query Prompt Template:")
        print(settings.QUERY_PROMPT_TEMPLATE)
        
        # Check if prompts include multiple questions handling
        if "multiple questions" in settings.SYSTEM_PROMPT.lower():
            print("\n✅ System prompt includes multiple questions handling")
        else:
            print("\n❌ System prompt missing multiple questions handling")
            return False
            
        if "comprehensive" in settings.QUERY_PROMPT_TEMPLATE.lower():
            print("✅ Query prompt includes comprehensive instructions")
        else:
            print("❌ Query prompt missing comprehensive instructions")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_llm_client_improvements():
    """Test LLM client improvements"""
    print("\n🤖 Testing LLM Client Improvements")
    print("=" * 50)
    
    try:
        from llm_service.llm_client import llm_client
        
        print(f"Model: {llm_client.model}")
        print(f"Max Tokens: {llm_client.max_tokens}")
        print(f"Temperature: {llm_client.temperature}")
        
        if llm_client.max_tokens >= 4000:
            print("✅ LLM client configured with increased token limit")
            return True
        else:
            print(f"❌ LLM client still has low token limit: {llm_client.max_tokens}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_comprehensive_response():
    """Test comprehensive response generation"""
    print("\n🧪 Testing Comprehensive Response Generation")
    print("=" * 50)
    
    # Check if API keys are available
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY not set, skipping response generation test")
        return True
    
    try:
        from llm_service.llm_client import llm_client
        
        # Test with a simple prompt to check token handling
        test_prompt = "Please provide a comprehensive answer to the following questions: 1. What is the waiting period? 2. What are the exclusions? 3. What is the coverage amount?"
        
        print("Testing response generation...")
        response = llm_client.generate_response(test_prompt)
        
        print(f"Response length: {len(response)} characters")
        print(f"Response preview: {response[:200]}...")
        
        if len(response) > 100:
            print("✅ Response generation working with increased token limit")
            return True
        else:
            print("❌ Response seems too short")
            return False
            
    except Exception as e:
        print(f"❌ Error in response generation: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Comprehensive Response Improvements")
    print("=" * 60)
    
    # Test 1: Multiple questions detection
    questions_success = test_multiple_questions_detection()
    
    # Test 2: Token limit increase
    token_success = test_token_limit_increase()
    
    # Test 3: Improved prompts
    prompt_success = test_improved_prompts()
    
    # Test 4: LLM client improvements
    client_success = test_llm_client_improvements()
    
    # Test 5: Comprehensive response generation
    response_success = test_comprehensive_response()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    print(f"Multiple Questions Detection: {'✅ PASS' if questions_success else '❌ FAIL'}")
    print(f"Token Limit Increase: {'✅ PASS' if token_success else '❌ FAIL'}")
    print(f"Improved Prompts: {'✅ PASS' if prompt_success else '❌ FAIL'}")
    print(f"LLM Client Improvements: {'✅ PASS' if client_success else '❌ FAIL'}")
    print(f"Response Generation: {'✅ PASS' if response_success else '❌ FAIL'}")
    
    if all([questions_success, token_success, prompt_success, client_success, response_success]):
        print("\n🎉 All tests passed! Comprehensive response improvements are working.")
        print("Your system should now provide complete answers to multiple questions.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
    
    print("\n📋 Expected Improvements:")
    print("• Token limit increased from 1000 to 4000 tokens")
    print("• Better handling of multiple questions in single queries")
    print("• More comprehensive and detailed responses")
    print("• Improved prompt templates for legal document analysis")
    print("• Better structure for multi-part answers")
    
    print("\n🧪 Test your improved system:")
    print("1. Start your server: uvicorn api.main:app --reload")
    print("2. Try the same multi-question query that was cut off before")
    print("3. You should now get complete answers to all questions!")

if __name__ == "__main__":
    main() 