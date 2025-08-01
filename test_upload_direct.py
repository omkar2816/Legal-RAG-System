#!/usr/bin/env python3
"""
Direct test of upload functionality to verify the 422 error fix
"""
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_metadata_generation():
    """Test the metadata generation that was causing the 422 error"""
    print("Testing metadata generation...")
    
    # Read the sample contract
    with open('data/legal_docs/sample_contract.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Testing with sample contract ({len(content)} characters)")
    
    try:
        # Import the required modules
        from chunking.metadata_builder import metadata_builder
        from chunking.chunker import legal_chunker
        from ingestion.textCleaner import clean_text
        
        # Clean and chunk the text
        cleaned_text = clean_text(content)
        chunks = legal_chunker.chunk_text(cleaned_text, preserve_sections=True)
        
        print(f"Generated {len(chunks)} chunks")
        
        # Build metadata
        doc_metadata = {
            "doc_type": "contract",
            "title": "Sample Contract",
            "author": "Test Author"
        }
        
        chunk_metadata_list = metadata_builder.build_metadata(
            chunks=chunks,
            doc_id="test_doc_123",
            doc_metadata=doc_metadata
        )
        
        print(f"Generated metadata for {len(chunk_metadata_list)} chunks")
        
        # Check each chunk's metadata
        all_valid = True
        for i, metadata in enumerate(chunk_metadata_list):
            if 'legal_terms' in metadata:
                if not isinstance(metadata['legal_terms'], list):
                    print(f"❌ Chunk {i}: legal_terms is {type(metadata['legal_terms'])} instead of list")
                    print(f"   Value: {metadata['legal_terms']}")
                    all_valid = False
                else:
                    print(f"✅ Chunk {i}: legal_terms is list with {len(metadata['legal_terms'])} items")
                    print(f"   Sample terms: {metadata['legal_terms'][:5] if metadata['legal_terms'] else 'None'}")
        
        if all_valid:
            print("✅ All metadata is valid - 422 error should be resolved!")
            return True
        else:
            print("❌ Some metadata is still invalid")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pinecone_metadata_format():
    """Test that metadata is in the correct format for Pinecone"""
    print("\nTesting Pinecone metadata format...")
    
    # Test with a simple text
    test_text = "This agreement is entered into by the parties. The contract contains terms and conditions."
    
    from chunking.metadata_builder import metadata_builder
    from chunking.chunker import legal_chunker
    from ingestion.textCleaner import clean_text
    
    # Process the text
    cleaned_text = clean_text(test_text)
    chunks = legal_chunker.chunk_text(cleaned_text, preserve_sections=True)
    
    # Build metadata
    chunk_metadata_list = metadata_builder.build_metadata(
        chunks=chunks,
        doc_id="test_doc_456",
        doc_metadata={"doc_type": "test", "title": "Test Document"}
    )
    
    # Check each metadata field
    for i, metadata in enumerate(chunk_metadata_list):
        print(f"\nChunk {i} metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {type(value)} = {value}")
            
            # Check if value is Pinecone-compatible
            if isinstance(value, (str, int, float, bool, list)):
                print(f"    ✅ {key} is Pinecone-compatible")
            else:
                print(f"    ❌ {key} is NOT Pinecone-compatible: {type(value)}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("DIRECT UPLOAD TESTING")
    print("=" * 60)
    
    # Test 1: Metadata generation
    print("\n1. Testing metadata generation...")
    metadata_ok = test_metadata_generation()
    
    # Test 2: Pinecone metadata format
    print("\n2. Testing Pinecone metadata format...")
    format_ok = test_pinecone_metadata_format()
    
    print("\n" + "=" * 60)
    if metadata_ok and format_ok:
        print("✅ ALL TESTS PASSED!")
        print("The 422 validation error should now be resolved.")
        print("You can now test the upload with the server.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("There may still be issues with the metadata format.")
    print("=" * 60) 