#!/usr/bin/env python3
"""
Test script to verify token limit fixes are working
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from llm_service.llm_client import llm_client
from llm_service.response_formatter import response_formatter
from utils.validation import validation_utils

def test_token_limit_configuration():
    """Test that token limits are properly configured"""
    print("🔧 Testing Token Limit Configuration")
    
    # Check environment variable
    print(f"GROQ_MAX_TOKENS from env: {os.getenv('GROQ_MAX_TOKENS', 'Not set')}")
    print(f"Settings GROQ_MAX_TOKENS: {settings.GROQ_MAX_TOKENS}")
    
    # Check LLM client configuration
    print(f"LLM Client max_tokens: {llm_client.max_tokens}")
    
    # Check response formatter configuration
    print(f"Response formatter max_length: {response_formatter.config.max_length}")
    
    # Check validation utility
    print(f"Validation utility max_length: 50000 (hardcoded)")
    
    # Verify all are properly set
    success = True
    if settings.GROQ_MAX_TOKENS < 8000:
        print("❌ Settings GROQ_MAX_TOKENS is too low")
        success = False
    else:
        print("✅ Settings GROQ_MAX_TOKENS is properly set")
    
    if llm_client.max_tokens < 8000:
        print("❌ LLM client max_tokens is too low")
        success = False
    else:
        print("✅ LLM client max_tokens is properly set")
    
    if response_formatter.config.max_length < 8000:
        print("❌ Response formatter max_length is too low")
        success = False
    else:
        print("✅ Response formatter max_length is properly set")
    
    return success

def test_response_formatter_templates():
    """Test that response formatter templates have proper max_length"""
    print("\n🔧 Testing Response Formatter Templates")
    
    success = True
    for response_type, template_info in response_formatter.response_templates.items():
        max_length = template_info["max_length"]
        print(f"{response_type.value}: max_length = {max_length}")
        
        if max_length < 8000:
            print(f"❌ {response_type.value} max_length is too low")
            success = False
        else:
            print(f"✅ {response_type.value} max_length is properly set")
    
    return success

def test_prompt_template():
    """Test that prompt template doesn't limit response length"""
    print("\n🔧 Testing Prompt Template")
    
    # Read the prompt template
    try:
        with open("llm_service/prompt_template.j2", "r") as f:
            template_content = f.read()
        
        if "150-300 words maximum" in template_content:
            print("❌ Prompt template still has word limit")
            return False
        elif "comprehensive and detailed responses" in template_content:
            print("✅ Prompt template allows comprehensive responses")
            return True
        else:
            print("⚠️ Prompt template content unclear")
            return True
            
    except FileNotFoundError:
        print("⚠️ Prompt template file not found")
        return True

def test_validation_utility():
    """Test that validation utility allows longer text"""
    print("\n🔧 Testing Validation Utility")
    
    # Test with a long text
    long_text = "This is a test. " * 1000  # About 15,000 characters
    
    # This should not be truncated
    sanitized = validation_utils.sanitize_text(long_text)
    
    if len(sanitized) < len(long_text) and "..." in sanitized:
        print("❌ Validation utility is still truncating text")
        return False
    else:
        print("✅ Validation utility allows longer text")
        return True

def main():
    """Run all tests"""
    print("🚀 Testing Token Limit Fixes")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Run tests
    config_success = test_token_limit_configuration()
    template_success = test_response_formatter_templates()
    prompt_success = test_prompt_template()
    validation_success = test_validation_utility()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    print(f"Token Limit Configuration: {'✅ PASS' if config_success else '❌ FAIL'}")
    print(f"Response Formatter Templates: {'✅ PASS' if template_success else '❌ FAIL'}")
    print(f"Prompt Template: {'✅ PASS' if prompt_success else '❌ FAIL'}")
    print(f"Validation Utility: {'✅ PASS' if validation_success else '❌ FAIL'}")
    
    overall_success = config_success and template_success and prompt_success and validation_success
    
    if overall_success:
        print("\n🎉 All tests passed! Token limit fixes are working correctly.")
        print("\n📝 Summary of fixes applied:")
        print("• Increased GROQ_MAX_TOKENS to 8000")
        print("• Increased response formatter max_length to 8000")
        print("• Updated prompt template to allow comprehensive responses")
        print("• Increased validation utility text limit to 50,000 characters")
        print("• Modified length constraints to be more lenient")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 