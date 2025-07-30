#!/usr/bin/env python3
"""
Test script to verify Pinecone setup with the new API
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def test_pinecone_setup():
    """Test Pinecone setup and connectivity"""
    
    print("=" * 50)
    print("PINECONE SETUP TEST")
    print("=" * 50)
    print()
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        return False
    
    try:
        # Import settings
        from config.settings import settings
        
        print("🔍 Testing configuration...")
        
        # Check required settings
        if not settings.PINECONE_API_KEY:
            print("❌ PINECONE_API_KEY not found in .env")
            return False
        
        if not settings.OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY not found in .env")
            return False
        
        print("✅ Environment variables loaded")
        print(f"  Pinecone API Key: {settings.PINECONE_API_KEY[:10]}...")
        print(f"  Environment: {settings.PINECONE_ENVIRONMENT}")
        print(f"  Index Name: {settings.PINECONE_INDEX_NAME}")
        print(f"  Dimension: {settings.PINECONE_DIMENSION}")
        print()
        
        # Test Pinecone connection
        print("🔌 Testing Pinecone connection...")
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        print("✅ Pinecone client initialized")
        
        # List indexes
        indexes = pc.list_indexes().names()
        print(f"  Available indexes: {indexes}")
        
        # Check if our index exists
        if settings.PINECONE_INDEX_NAME in indexes:
            print(f"✅ Index '{settings.PINECONE_INDEX_NAME}' exists")
            
            # Test index connection
            try:
                index = pc.Index(settings.PINECONE_INDEX_NAME)
                stats = index.describe_index_stats()
                print(f"✅ Index is accessible")
                print(f"  Total vectors: {stats.get('total_vector_count', 0)}")
                print(f"  Dimension: {stats.get('dimension', 'N/A')}")
                print(f"  Metric: {stats.get('metric', 'N/A')}")
            except Exception as e:
                print(f"⚠️  Index exists but may still be initializing: {e}")
        else:
            print(f"⚠️  Index '{settings.PINECONE_INDEX_NAME}' not found")
            print("   You may need to create it using: python create_pinecone_index.py")
        
        print()
        print("=" * 50)
        print("✅ PINECONE SETUP TEST COMPLETED")
        print("=" * 50)
        print()
        print("If all tests passed, your Pinecone setup is ready!")
        print("You can now run the application: uvicorn api.main:app --reload")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print()
        print("Common issues:")
        print("1. Invalid Pinecone API key")
        print("2. Network connectivity issues")
        print("3. Pinecone service unavailable")
        return False

if __name__ == "__main__":
    success = test_pinecone_setup()
    if not success:
        sys.exit(1) 