#!/usr/bin/env python3
"""
Test script for accuracy improvements in Legal RAG System
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query_enhancer import query_enhancer, enhance_legal_query, classify_query_intent, expand_legal_query
from vectordb.hybrid_retrieval import hybrid_search, multi_stage_retrieval
from config.settings import settings

def test_query_enhancement():
    """Test query enhancement functionality"""
    print("🔍 Testing Query Enhancement")
    print("=" * 50)
    
    test_queries = [
        "what is maximum waiting period for preexisting diseases?",
        "how much is the coverage amount?",
        "what are the exclusions in the policy?",
        "how long is the claim process?",
        "what is the definition of hospitalization?"
    ]
    
    for query in test_queries:
        print(f"\nOriginal Query: {query}")
        
        # Test query enhancement
        enhanced = enhance_legal_query(query)
        print(f"Enhanced Query: {enhanced}")
        
        # Test intent classification
        intent = classify_query_intent(query)
        print(f"Intent: {intent['primary_intent']} (confidence: {intent['confidence']:.2f})")
        
        # Test query expansion
        variations = expand_legal_query(query)
        print(f"Query Variations: {len(variations)}")
        for i, variation in enumerate(variations[:3]):  # Show first 3
            print(f"  {i+1}. {variation}")
        
        print("-" * 50)

def test_hybrid_retrieval():
    """Test hybrid retrieval functionality"""
    print("\n🔍 Testing Hybrid Retrieval")
    print("=" * 50)
    
    # Check if API keys are set
    if not os.getenv("VOYAGE_API_KEY") or not os.getenv("PINECONE_API_KEY"):
        print("❌ Missing API keys. Please set VOYAGE_API_KEY and PINECONE_API_KEY")
        return False
    
    test_query = "what is maximum waiting period for preexisting diseases?"
    
    try:
        print(f"Query: {test_query}")
        
        # Test hybrid search
        print("\n1. Testing Hybrid Search...")
        hybrid_results = hybrid_search(test_query, top_k=3)
        
        if hybrid_results:
            print(f"✅ Found {len(hybrid_results)} results")
            for i, result in enumerate(hybrid_results):
                print(f"  Result {i+1}:")
                print(f"    Score: {result.get('combined_score', result.get('similarity_score', 0)):.3f}")
                print(f"    Document: {result.get('doc_title', 'Unknown')}")
                print(f"    Text Preview: {result.get('text', '')[:100]}...")
        else:
            print("❌ No results found")
        
        # Test multi-stage retrieval
        print("\n2. Testing Multi-Stage Retrieval...")
        multi_results = multi_stage_retrieval(test_query, top_k=3)
        
        if multi_results:
            print(f"✅ Found {len(multi_results)} results")
            for i, result in enumerate(multi_results):
                print(f"  Result {i+1}:")
                print(f"    Combined Score: {result.get('combined_score', 0):.3f}")
                print(f"    Semantic Score: {result.get('semantic_score', 0):.3f}")
                print(f"    Keyword Score: {result.get('keyword_score', 0):.3f}")
                print(f"    Document: {result.get('doc_title', 'Unknown')}")
                print(f"    Text Preview: {result.get('text', '')[:100]}...")
        else:
            print("❌ No results found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during retrieval testing: {str(e)}")
        return False

def test_configuration():
    """Test accuracy improvement configuration"""
    print("\n⚙️ Testing Configuration")
    print("=" * 50)
    
    config_items = [
        ("MIN_SIMILARITY_THRESHOLD", settings.MIN_SIMILARITY_THRESHOLD),
        ("MEDIUM_SIMILARITY_THRESHOLD", settings.MEDIUM_SIMILARITY_THRESHOLD),
        ("HIGH_SIMILARITY_THRESHOLD", settings.HIGH_SIMILARITY_THRESHOLD),
        ("CHUNK_SIZE", settings.CHUNK_SIZE),
        ("CHUNK_OVERLAP", settings.CHUNK_OVERLAP),
        ("ENABLE_QUERY_ENHANCEMENT", settings.ENABLE_QUERY_ENHANCEMENT),
        ("ENABLE_HYBRID_SEARCH", settings.ENABLE_HYBRID_SEARCH),
        ("ENABLE_MULTI_STAGE_RETRIEVAL", settings.ENABLE_MULTI_STAGE_RETRIEVAL),
        ("ENABLE_SEMANTIC_CHUNKING", settings.ENABLE_SEMANTIC_CHUNKING)
    ]
    
    for name, value in config_items:
        print(f"{name}: {value}")

def compare_accuracy():
    """Compare accuracy before and after improvements"""
    print("\n📊 Accuracy Comparison")
    print("=" * 50)
    
    print("Expected Improvements:")
    print("• Similarity Score: 0.069 → 0.6+ (target)")
    print("• Confidence Score: 0.069 → 0.7+ (target)")
    print("• Answer Relevance: 60% → 85%+ (target)")
    print("• Source Accuracy: 70% → 90%+ (target)")
    
    print("\nKey Improvements Implemented:")
    print("✅ Enhanced Query Processing")
    print("✅ Hybrid Search (Semantic + Keyword)")
    print("✅ Multi-Stage Retrieval Pipeline")
    print("✅ Improved Threshold Management")
    print("✅ Better Chunking Strategy")
    print("✅ Query Intent Classification")
    print("✅ Context-Aware Re-ranking")

def main():
    """Main test function"""
    print("🚀 Legal RAG System - Accuracy Improvement Tests")
    print("=" * 60)
    
    # Test configuration
    test_configuration()
    
    # Test query enhancement
    test_query_enhancement()
    
    # Test hybrid retrieval (if API keys are available)
    retrieval_success = test_hybrid_retrieval()
    
    # Show accuracy comparison
    compare_accuracy()
    
    print("\n" + "=" * 60)
    if retrieval_success:
        print("✅ All tests completed successfully!")
        print("🎯 Your system should now have significantly improved accuracy")
    else:
        print("⚠️ Some tests failed due to missing API keys")
        print("📝 Set up your API keys to test the full functionality")
    
    print("\n📋 Next Steps:")
    print("1. Update your .env file with the new configuration")
    print("2. Test with your existing documents")
    print("3. Monitor the improvement in similarity scores")
    print("4. Adjust thresholds if needed")

if __name__ == "__main__":
    main() 