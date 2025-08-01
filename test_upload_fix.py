#!/usr/bin/env python3
"""
Test script to verify the upload fix works
"""
import os
import sys
import tempfile
import shutil

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chunking.metadata_builder import metadata_builder
from chunking.chunker import legal_chunker
from ingestion.textCleaner import clean_text

def test_upload_processing():
    """Test the complete upload processing pipeline"""
    print("Testing upload processing pipeline...")
    
    # Read the sample contract
    with open('data/legal_docs/sample_contract.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"Original text length: {len(text)} characters")
    
    # Clean text
    cleaned_text = clean_text(text)
    print(f"Cleaned text length: {len(cleaned_text)} characters")
    
    # Chunk text
    chunks = legal_chunker.chunk_text(cleaned_text, preserve_sections=True)
    print(f"Generated {len(chunks)} chunks")
    
    # Build metadata for chunks
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
    
    # Check if any metadata has the old dictionary format
    problematic_chunks = []
    for i, metadata in enumerate(chunk_metadata_list):
        if 'legal_terms' in metadata:
            if not isinstance(metadata['legal_terms'], list):
                problematic_chunks.append(i)
                print(f"❌ Chunk {i}: legal_terms is {type(metadata['legal_terms'])} instead of list")
            else:
                print(f"✅ Chunk {i}: legal_terms is list with {len(metadata['legal_terms'])} items")
    
    if problematic_chunks:
        print(f"❌ Found {len(problematic_chunks)} chunks with problematic legal_terms format")
        return False
    else:
        print("✅ All chunks have correct legal_terms format (list of strings)")
        return True

def test_metadata_consistency():
    """Test that metadata is consistent across different documents"""
    print("\nTesting metadata consistency...")
    
    test_texts = [
        "This agreement is entered into by the parties.",
        "The contract contains terms and conditions for employment.",
        "WHEREAS, the parties desire to enter into this agreement; NOW, THEREFORE, the parties agree as follows."
    ]
    
    for i, text in enumerate(test_texts):
        analysis = metadata_builder._analyze_legal_terms(text)
        print(f"Text {i+1}: legal_terms type = {type(analysis['legal_terms'])}, count = {len(analysis['legal_terms'])}")
        
        if not isinstance(analysis['legal_terms'], list):
            print(f"❌ Text {i+1} has incorrect legal_terms format")
            return False
    
    print("✅ All test texts have correct legal_terms format")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING UPLOAD FIX")
    print("=" * 60)
    
    # Test 1: Metadata builder fix
    print("\n1. Testing metadata builder fix...")
    from test_metadata_fix import test_metadata_fix
    test_metadata_fix()
    
    # Test 2: Upload processing pipeline
    print("\n2. Testing upload processing pipeline...")
    pipeline_ok = test_upload_processing()
    
    # Test 3: Metadata consistency
    print("\n3. Testing metadata consistency...")
    consistency_ok = test_metadata_consistency()
    
    print("\n" + "=" * 60)
    if pipeline_ok and consistency_ok:
        print("✅ ALL TESTS PASSED - Upload fix is working correctly!")
        print("The 422 validation error should now be resolved.")
    else:
        print("❌ SOME TESTS FAILED - There may still be issues.")
    print("=" * 60) 