#!/usr/bin/env python3
"""
Test script to verify document processing and chunking
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from chunking.chunker import legal_chunker
from chunking.metadata_builder import metadata_builder
from embeddings.mock_embed_client import mock_embedding_client

def test_document_processing():
    """Test document processing with sample files"""
    print("=" * 60)
    print("DOCUMENT PROCESSING TEST")
    print("=" * 60)
    
    # Test with sample contract
    contract_path = "data/legal_docs/sample_contract.txt"
    
    if not os.path.exists(contract_path):
        print(f"❌ Sample contract not found: {contract_path}")
        return
    
    print(f"📄 Processing: {contract_path}")
    
    # Read the document
    with open(contract_path, 'r', encoding='utf-8') as f:
        document_text = f.read()
    
    print(f"📊 Document size: {len(document_text)} characters")
    
    # Clean the text
    cleaned_text = legal_chunker.clean_text(document_text)
    print(f"🧹 Cleaned text size: {len(cleaned_text)} characters")
    
    # Chunk the text
    chunks = legal_chunker.chunk_text(cleaned_text, preserve_sections=True)
    print(f"✂️  Generated {len(chunks)} chunks")
    
    # Display chunk information
    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"\nChunk {i+1}:")
        print(f"  Text preview: {chunk['text'][:100]}...")
        print(f"  Word count: {chunk.get('word_count', 0)}")
        print(f"  Section: {chunk.get('section_title', 'N/A')}")
    
    # Build metadata
    doc_metadata = {
        "doc_type": "employment_agreement",
        "title": "Sample Employment Contract",
        "author": "Legal Department"
    }
    
    metadata_list = metadata_builder.build_metadata(
        chunks=chunks,
        doc_id="test_contract_001",
        doc_metadata=doc_metadata
    )
    
    print(f"\n📋 Generated metadata for {len(metadata_list)} chunks")
    
    # Test mock embeddings
    print("\n🧠 Testing mock embeddings...")
    chunk_texts = [chunk['text'] for chunk in chunks]
    
    try:
        embeddings = mock_embedding_client.get_embeddings(chunk_texts)
        print(f"✅ Generated {len(embeddings)} mock embeddings")
        print(f"   Embedding dimension: {len(embeddings[0]) if embeddings else 0}")
        
        # Check if embeddings are non-zero
        non_zero_count = sum(1 for emb in embeddings if any(val != 0 for val in emb))
        print(f"   Non-zero embeddings: {non_zero_count}/{len(embeddings)}")
        
    except Exception as e:
        print(f"❌ Mock embedding failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Document processing test completed!")
    print("=" * 60)

def test_upload_processing():
    """Test the complete upload and processing pipeline"""
    print("\n" + "=" * 60)
    print("UPLOAD PROCESSING PIPELINE TEST")
    print("=" * 60)
    
    import requests
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Upload a test document
    contract_path = "data/legal_docs/sample_contract.txt"
    if not os.path.exists(contract_path):
        print(f"❌ Test document not found: {contract_path}")
        return
    
    print(f"📤 Uploading test document...")
    
    try:
        with open(contract_path, 'rb') as file:
            files = {'file': file}
            data = {
                'doc_type': 'employment_agreement',
                'doc_title': 'Test Employment Contract'
            }
            
            response = requests.post(
                "http://localhost:8000/ingest/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful: {result.get('message', 'Uploaded')}")
                print(f"   File path: {result.get('file_path', 'N/A')}")
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_document_processing()
    test_upload_processing() 