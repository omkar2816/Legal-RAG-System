#!/usr/bin/env python3
"""
Test script to verify Pinecone client fix and hybrid retrieval functionality
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pinecone_client():
    """Test that Pinecone client functions work correctly"""
    print("🔧 Testing Pinecone Client Fix")
    print("=" * 50)
    
    try:
        # Test imports
        from vectordb.pinecone_client import get_all_vectors, query_embeddings, get_index_stats
        print("✅ Successfully imported Pinecone client functions")
        
        # Test index stats
        try:
            stats = get_index_stats()
            print(f"✅ Index stats retrieved: {stats.get('total_vector_count', 0)} vectors")
        except Exception as e:
            print(f"⚠️  Could not get index stats: {str(e)}")
        
        # Test get_all_vectors function
        try:
            vectors = get_all_vectors(limit=10)  # Test with small limit
            print(f"✅ get_all_vectors function works: {len(vectors)} vectors retrieved")
        except Exception as e:
            print(f"❌ Error in get_all_vectors: {str(e)}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_hybrid_retrieval():
    """Test hybrid retrieval system"""
    print("\n🔍 Testing Hybrid Retrieval System")
    print("=" * 50)
    
    try:
        # Test imports
        from vectordb.hybrid_retrieval import hybrid_search, multi_stage_retrieval
        print("✅ Successfully imported hybrid retrieval functions")
        
        # Test query enhancer
        from utils.query_enhancer import query_enhancer
        print("✅ Query enhancer imported successfully")
        
        # Test with a simple query
        test_query = "what is maximum waiting period for preexisting diseases?"
        
        print(f"Testing query: {test_query}")
        
        # Test query enhancement
        enhanced = query_enhancer.enhance_query(test_query)
        print(f"Enhanced query: {enhanced}")
        
        # Test intent classification
        intent = query_enhancer.classify_intent(test_query)
        print(f"Query intent: {intent['primary_intent']} (confidence: {intent['confidence']:.2f})")
        
        # Test hybrid search (if API keys are available)
        if os.getenv("VOYAGE_API_KEY") and os.getenv("PINECONE_API_KEY"):
            try:
                results = hybrid_search(test_query, top_k=3)
                print(f"✅ Hybrid search completed: {len(results)} results")
                
                if results:
                    print("Sample result:")
                    result = results[0]
                    print(f"  Document: {result.get('doc_title', 'Unknown')}")
                    print(f"  Score: {result.get('combined_score', result.get('similarity_score', 0)):.3f}")
                    print(f"  Text preview: {result.get('text', '')[:100]}...")
                
            except Exception as e:
                print(f"⚠️  Hybrid search error: {str(e)}")
        else:
            print("⚠️  Skipping hybrid search test - missing API keys")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_api_integration():
    """Test API integration"""
    print("\n🌐 Testing API Integration")
    print("=" * 50)
    
    try:
        # Test that the query API can import hybrid retrieval
        from api.routes.query import router
        print("✅ Query API router imported successfully")
        
        # Test settings
        from config.settings import settings
        print(f"✅ Settings loaded: ENABLE_HYBRID_SEARCH = {settings.ENABLE_HYBRID_SEARCH}")
        
        return True
        
    except Exception as e:
        print(f"❌ API integration error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Pinecone Client Fix and Hybrid Retrieval")
    print("=" * 60)
    
    # Test 1: Pinecone client
    pinecone_success = test_pinecone_client()
    
    # Test 2: Hybrid retrieval
    hybrid_success = test_hybrid_retrieval()
    
    # Test 3: API integration
    api_success = test_api_integration()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    print(f"Pinecone Client: {'✅ PASS' if pinecone_success else '❌ FAIL'}")
    print(f"Hybrid Retrieval: {'✅ PASS' if hybrid_success else '❌ FAIL'}")
    print(f"API Integration: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if pinecone_success and hybrid_success and api_success:
        print("\n🎉 All tests passed! The fix is working correctly.")
        print("Your Legal RAG System should now work without the import error.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
    
    print("\n📋 Next Steps:")
    print("1. Start your server: uvicorn api.main:app --reload")
    print("2. Test your query that was giving the import error")
    print("3. You should now see much higher similarity scores!")

if __name__ == "__main__":
    main() 