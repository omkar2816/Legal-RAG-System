#!/usr/bin/env python3
"""
Test script for the Legal RAG System
This script demonstrates the basic functionality of the system
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from chunking.chunker import legal_chunker
from chunking.metadata_builder import metadata_builder
from embeddings.embed_client import embedding_client
from llm_service.llm_client import llm_client
from utils.validation import validation_utils

def test_chunking():
    """Test the legal document chunking functionality"""
    print("Testing Legal Document Chunking...")
    
    # Sample legal text
    sample_text = """
    EMPLOYMENT AGREEMENT
    
    This Employment Agreement (the "Agreement") is entered into as of January 15, 2024, by and between:
    
    ABC Corporation, a Delaware corporation (the "Company")
    and
    John Smith, an individual (the "Employee")
    
    ARTICLE I: EMPLOYMENT
    
    Section 1.1: Position and Duties
    The Company hereby employs the Employee as Senior Software Engineer, and the Employee accepts such employment.
    
    Section 1.2: Term of Employment
    The Employee's employment under this Agreement shall commence on February 1, 2024 and shall continue until terminated.
    
    ARTICLE II: COMPENSATION
    
    Section 2.1: Base Salary
    The Company shall pay the Employee an annual base salary of $120,000, payable in accordance with the Company's normal payroll practices.
    """
    
    # Clean and chunk the text
    cleaned_text = legal_chunker.clean_text(sample_text)
    chunks = legal_chunker.chunk_text(cleaned_text, preserve_sections=True)
    
    print(f"Generated {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
        print(f"Chunk {i+1}:")
        print(f"  Text: {chunk['text'][:100]}...")
        print(f"  Section: {chunk.get('section_title', 'N/A')}")
        print(f"  Word count: {chunk.get('word_count', 0)}")
        print()
    
    return chunks

def test_metadata_building(chunks):
    """Test metadata building functionality"""
    print("Testing Metadata Building...")
    
    # Build metadata for chunks
    doc_metadata = {
        "doc_type": "employment_agreement",
        "title": "Sample Employment Agreement",
        "author": "Legal Department"
    }
    
    metadata_list = metadata_builder.build_metadata(
        chunks=chunks,
        doc_id="test_doc_001",
        doc_metadata=doc_metadata
    )
    
    print(f"Generated metadata for {len(metadata_list)} chunks")
    for i, metadata in enumerate(metadata_list[:2]):  # Show first 2 metadata entries
        print(f"Metadata {i+1}:")
        print(f"  Doc ID: {metadata['doc_id']}")
        print(f"  Chunk ID: {metadata['chunk_id']}")
        print(f"  Legal density: {metadata.get('legal_density', 0):.3f}")
        print(f"  Is legal document: {metadata.get('is_legal_document', False)}")
        print()
    
    return metadata_list

def test_validation():
    """Test input validation functionality"""
    print("Testing Input Validation...")
    
    # Test query validation
    test_queries = [
        "What is the employee's salary?",
        "What are the termination provisions?",
        "",  # Empty query
        "Hi"  # Too short
    ]
    
    for query in test_queries:
        result = validation_utils.validate_query(query)
        print(f"Query: '{query}'")
        print(f"  Valid: {result['valid']}")
        if result['errors']:
            print(f"  Errors: {result['errors']}")
        if result['warnings']:
            print(f"  Warnings: {result['warnings']}")
        print()
    
    # Test file validation
    test_files = [
        ("document.pdf", 1024*1024, "application/pdf"),  # Valid
        ("document.txt", 1024*1024, "text/plain"),       # Valid
        ("document.exe", 1024*1024, "application/octet-stream"),  # Invalid
        ("document.pdf", 100*1024*1024, "application/pdf")  # Too large
    ]
    
    for filename, size, content_type in test_files:
        result = validation_utils.validate_file_upload(filename, size, content_type)
        print(f"File: {filename} ({size} bytes, {content_type})")
        print(f"  Valid: {result['valid']}")
        if result['errors']:
            print(f"  Errors: {result['errors']}")
        if result['warnings']:
            print(f"  Warnings: {result['warnings']}")
        print()

def test_embedding_generation():
    """Test embedding generation (mock)"""
    print("Testing Embedding Generation...")
    
    # Sample texts for embedding
    sample_texts = [
        "What is the employee's base salary?",
        "What are the termination provisions?",
        "What is the non-competition period?"
    ]
    
    print(f"Would generate embeddings for {len(sample_texts)} texts")
    print("Note: This would require valid Voyage AI API key")
    print()

def test_llm_response():
    """Test LLM response generation (mock)"""
    print("Testing LLM Response Generation...")
    
    # Sample context and question
    context = "The Company shall pay the Employee an annual base salary of $120,000, payable in accordance with the Company's normal payroll practices."
    question = "What is the employee's base salary?"
    
    print(f"Question: {question}")
    print(f"Context: {context}")
    print("Note: This would require valid Voyage AI API key")
    print()

def main():
    """Main test function"""
    print("=" * 60)
    print("LEGAL RAG SYSTEM - TEST SCRIPT")
    print("=" * 60)
    print()
    
    # Check if required environment variables are set
    print("Checking Configuration...")
    if not settings.validate_required_settings():
        print("❌ Missing required environment variables")
        print("Please set VOYAGE_API_KEY and PINECONE_API_KEY")
        print("You can copy env_template.txt to .env and fill in your keys")
        return
    else:
        print("✅ Configuration looks good")
    print()
    
    # Run tests
    try:
        chunks = test_chunking()
        metadata_list = test_metadata_building(chunks)
        test_validation()
        test_embedding_generation()
        test_llm_response()
        
        print("=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Set up your API keys in .env file")
        print("2. Run: uvicorn api.main:app --reload")
        print("3. Visit: http://localhost:8000/docs")
        print("4. Upload sample documents and test queries")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 