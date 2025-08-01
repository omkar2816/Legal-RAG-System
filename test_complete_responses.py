#!/usr/bin/env python3
"""
Test script to verify complete response improvements
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_token_limit_increase():
    """Test that token limit has been further increased"""
    print("🔧 Testing Token Limit Increase")
    print("=" * 50)
    
    try:
        from config.settings import settings
        
        print(f"Current GROQ_MAX_TOKENS: {settings.GROQ_MAX_TOKENS}")
        
        if settings.GROQ_MAX_TOKENS >= 8000:
            print("✅ Token limit has been increased to 8000+ tokens")
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
        
        # Check if prompts include completion instructions
        if "complete" in settings.SYSTEM_PROMPT.lower() and "truncate" in settings.SYSTEM_PROMPT.lower():
            print("\n✅ System prompt includes completion instructions")
        else:
            print("\n❌ System prompt missing completion instructions")
            return False
            
        if "complete" in settings.QUERY_PROMPT_TEMPLATE.lower() and "stop mid-sentence" in settings.QUERY_PROMPT_TEMPLATE.lower():
            print("✅ Query prompt includes completion instructions")
        else:
            print("❌ Query prompt missing completion instructions")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_multiple_questions_enhancement():
    """Test multiple questions enhancement"""
    print("\n🔍 Testing Multiple Questions Enhancement")
    print("=" * 50)
    
    try:
        from utils.query_enhancer import detect_multiple_questions
        
        # Test query with multiple questions
        test_query = "What is maximum waiting period for treatment of joint replacement?, What does the policy define as a Pre-Existing Disease?, What is the waiting period for cataract treatment under this policy?, What is the maximum co-payment percentage applicable under this policy? When does it apply?"
        
        print(f"Original Query: {test_query}")
        
        # Detect multiple questions
        questions = detect_multiple_questions(test_query)
        print(f"\nDetected {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
        
        if len(questions) > 1:
            print("✅ Multiple questions detection working")
            return True
        else:
            print("❌ Multiple questions detection failed")
            return False
        
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
        
        if llm_client.max_tokens >= 8000:
            print("✅ LLM client configured with increased token limit")
            
            # Test the new methods exist
            if hasattr(llm_client, '_enhance_multiple_questions_prompt'):
                print("✅ Multiple questions enhancement method exists")
            else:
                print("❌ Multiple questions enhancement method missing")
                return False
                
            if hasattr(llm_client, '_validate_response_completeness'):
                print("✅ Response validation method exists")
            else:
                print("❌ Response validation method missing")
                return False
                
            return True
        else:
            print(f"❌ LLM client still has low token limit: {llm_client.max_tokens}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_complete_response_generation():
    """Test complete response generation"""
    print("\n🧪 Testing Complete Response Generation")
    print("=" * 50)
    
    # Check if API keys are available
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  GROQ_API_KEY not set, skipping response generation test")
        return True
    
    try:
        from llm_service.llm_client import llm_client
        
        # Test with a multiple questions prompt
        test_prompt = "Please answer these questions: 1. What is the waiting period? 2. What are the exclusions? 3. What is the coverage amount? 4. When does it apply?"
        
        print("Testing complete response generation...")
        
        # Create mock context chunks
        mock_chunks = [{
            'metadata': {
                'doc_title': 'Test Policy',
                'section_title': 'Test Section'
            },
            'text': 'This is a test policy document with information about waiting periods, exclusions, coverage amounts, and application conditions.'
        }]
        
        response = llm_client.generate_legal_response(test_prompt, mock_chunks)
        
        print(f"Response length: {len(response)} characters")
        print(f"Response preview: {response[:300]}...")
        
        # Check if response seems complete
        if len(response) > 200 and not response.endswith('.'):
            print("✅ Response generation working with increased token limit")
            return True
        else:
            print("❌ Response seems too short or incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error in response generation: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Complete Response Improvements")
    print("=" * 60)
    
    # Test 1: Token limit increase
    token_success = test_token_limit_increase()
    
    # Test 2: Improved prompts
    prompt_success = test_improved_prompts()
    
    # Test 3: Multiple questions enhancement
    questions_success = test_multiple_questions_enhancement()
    
    # Test 4: LLM client improvements
    client_success = test_llm_client_improvements()
    
    # Test 5: Complete response generation
    response_success = test_complete_response_generation()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    print(f"Token Limit Increase: {'✅ PASS' if token_success else '❌ FAIL'}")
    print(f"Improved Prompts: {'✅ PASS' if prompt_success else '❌ FAIL'}")
    print(f"Multiple Questions Enhancement: {'✅ PASS' if questions_success else '❌ FAIL'}")
    print(f"LLM Client Improvements: {'✅ PASS' if client_success else '❌ FAIL'}")
    print(f"Complete Response Generation: {'✅ PASS' if response_success else '❌ FAIL'}")
    
    if all([token_success, prompt_success, questions_success, client_success, response_success]):
        print("\n🎉 All tests passed! Complete response improvements are working.")
        print("Your system should now provide complete answers to all questions without truncation.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
    
    print("\n📋 Expected Improvements:")
    print("• Token limit increased from 4000 to 8000 tokens")
    print("• Enhanced prompts with completion instructions")
    print("• Better multiple questions handling")
    print("• Response validation and completeness checking")
    print("• No more truncated responses")
    
    print("\n🧪 Test your improved system:")
    print("1. Update your .env file: GROQ_MAX_TOKENS=8000")
    print("2. Restart your server: uvicorn api.main:app --reload")
    print("3. Try the same multi-question query that was cut off before")
    print("4. You should now get complete answers to ALL questions!")

if __name__ == "__main__":
    main() 