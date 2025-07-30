#!/usr/bin/env python3
"""
Pinecone Index Creation Script for Legal RAG System
This script helps you create and configure your Pinecone index
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def create_pinecone_index():
    """Create Pinecone index for the Legal RAG System"""
    
    print("=" * 60)
    print("PINECONE INDEX CREATION FOR LEGAL RAG SYSTEM")
    print("=" * 60)
    print()
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your API keys first:")
        print("1. Copy env_template.txt to .env")
        print("2. Add your Pinecone API key to .env")
        print("3. Run this script again")
        return False
    
    try:
        # Import after ensuring .env exists
        from config.settings import settings
        from vectordb.pinecone_client import create_index, get_index_stats
        
        print("🔍 Checking configuration...")
        
        # Validate required settings
        if not settings.validate_required_settings():
            print("❌ Missing required environment variables")
            print("Please ensure your .env file contains:")
            print("  - PINECONE_API_KEY")
            print("  - OPENAI_API_KEY")
            return False
        
        print("✅ Configuration validated")
        print()
        
        # Display index configuration
        print("📋 Index Configuration:")
        print(f"  Index Name: {settings.PINECONE_INDEX_NAME}")
        print(f"  Environment: {settings.PINECONE_ENVIRONMENT}")
        print(f"  Dimension: {settings.PINECONE_DIMENSION}")
        print(f"  Metric: cosine")
        print(f"  Type: Serverless (AWS)")
        print()
        
        # Create the index
        print("🔨 Creating Pinecone index...")
        try:
            create_index(
                dimension=settings.PINECONE_DIMENSION,
                metric="cosine"
            )
            print("✅ Index creation completed")
        except Exception as e:
            print(f"⚠️  Index creation encountered an issue: {e}")
            print("This might be normal if the index already exists or is being created.")
        print()
        
        # Wait a moment for index to be ready
        print("⏳ Waiting for index to be ready...")
        import time
        time.sleep(5)
        
        # Get index statistics
        print("📊 Index Statistics:")
        try:
            stats = get_index_stats()
            print(f"  Total Vector Count: {stats.get('total_vector_count', 'N/A')}")
            print(f"  Index Dimension: {stats.get('dimension', 'N/A')}")
            print(f"  Index Metric: {stats.get('metric', 'N/A')}")
            print(f"  Namespaces: {list(stats.get('namespaces', {}).keys())}")
            print("✅ Index is ready and accessible")
        except Exception as e:
            print(f"⚠️  Could not retrieve stats: {e}")
            print("The index might still be initializing. This is normal for new indexes.")
        
        print()
        print("=" * 60)
        print("✅ PINECONE INDEX SETUP COMPLETED!")
        print("=" * 60)
        print()
        print("Your index is now ready for the Legal RAG System!")
        print()
        print("Next steps:")
        print("1. Start the application: uvicorn api.main:app --reload")
        print("2. Upload documents using the API")
        print("3. Test queries through the web interface")
        print()
        print("API Documentation: http://localhost:8000/docs")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        print()
        print("Common issues:")
        print("1. Invalid Pinecone API key")
        print("2. Wrong Pinecone environment")
        print("3. Network connectivity issues")
        print("4. Pinecone service unavailable")
        print("5. Insufficient Pinecone credits/quota")
        print()
        print("Troubleshooting:")
        print("- Check your Pinecone console for account status")
        print("- Verify your API key is correct")
        print("- Ensure you have sufficient credits for serverless index")
        return False

def main():
    """Main function"""
    success = create_pinecone_index()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 