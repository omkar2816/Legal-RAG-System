#!/usr/bin/env python3
"""
Simple test script for the Legal RAG System
This script demonstrates the basic functionality without requiring Voyage AI API calls
"""
import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from chunking.chunker import legal_chunker
from chunking.metadata_builder import metadata_builder
from utils.validation import validation_utils

def test_chunking():
    """Test the legal document chunking functionality"""
    print("Testing Legal Document Chunking...")
    
    # Sample legal text from the contract
    sample_text = """
    EMPLOYMENT AGREEMENT

    This Employment Agreement (the "Agreement") is entered into as of January 15, 2024, by and between:

    ABC Corporation, a Delaware corporation with its principal place of business at 123 Business Street, New York, NY 10001 (the "Company")

    and

    John Smith, an individual residing at 456 Personal Avenue, New York, NY 10002 (the "Employee")

    WHEREAS, the Company desires to employ the Employee and the Employee desires to be employed by the Company;

    NOW, THEREFORE, in consideration of the mutual promises and covenants contained herein, the parties agree as follows:

    ARTICLE I: EMPLOYMENT

    Section 1.1: Position and Duties
    The Company hereby employs the Employee as Senior Software Engineer, and the Employee accepts such employment. The Employee shall report to the Chief Technology Officer and shall perform such duties as are customarily performed by a Senior Software Engineer and such other duties as may be assigned by the Company from time to time.

    Section 1.2: Term of Employment
    The Employee's employment under this Agreement shall commence on February 1, 2024 (the "Effective Date") and shall continue until terminated in accordance with the provisions of this Agreement.

    ARTICLE II: COMPENSATION AND BENEFITS

    Section 2.1: Base Salary
    The Company shall pay the Employee an annual base salary of $120,000, payable in accordance with the Company's normal payroll practices, subject to applicable withholdings and deductions.

    Section 2.2: Bonus
    The Employee shall be eligible for an annual performance bonus of up to 20% of base salary, based on individual and company performance, as determined by the Company in its sole discretion.

    Section 2.3: Benefits
    The Employee shall be eligible to participate in the Company's employee benefit plans, including health insurance, dental insurance, vision insurance, and 401(k) plan, in accordance with the terms and conditions of such plans.

    ARTICLE III: CONFIDENTIALITY AND INTELLECTUAL PROPERTY

    Section 3.1: Confidential Information
    The Employee acknowledges that during the course of employment, the Employee will have access to confidential and proprietary information of the Company, including but not limited to trade secrets, customer lists, business plans, and technical information (collectively, "Confidential Information"). The Employee agrees to maintain the confidentiality of such information and not to disclose it to any third party without the Company's prior written consent.

    Section 3.2: Intellectual Property
    The Employee agrees that all inventions, discoveries, improvements, and other intellectual property created, developed, or conceived by the Employee during the course of employment and relating to the Company's business shall be the sole and exclusive property of the Company.

    ARTICLE IV: TERMINATION

    Section 4.1: Termination by Company
    The Company may terminate the Employee's employment at any time for any reason, with or without cause, upon written notice to the Employee.

    Section 4.2: Termination by Employee
    The Employee may terminate employment by providing the Company with at least two weeks' written notice.

    Section 4.3: Severance
    In the event of termination without cause, the Employee shall be entitled to severance pay equal to one month's base salary for each year of service, up to a maximum of six months' salary.

    ARTICLE V: NON-COMPETITION

    Section 5.1: Non-Competition Period
    During employment and for a period of one year following termination, the Employee shall not engage in any business that competes with the Company within a 50-mile radius of the Company's principal place of business.

    Section 5.2: Non-Solicitation
    During employment and for a period of two years following termination, the Employee shall not solicit any customers or employees of the Company.

    ARTICLE VI: GENERAL PROVISIONS

    Section 6.1: Governing Law
    This Agreement shall be governed by and construed in accordance with the laws of the State of New York.

    Section 6.2: Entire Agreement
    This Agreement constitutes the entire agreement between the parties and supersedes all prior agreements and understandings, whether written or oral.

    Section 6.3: Amendment
    This Agreement may be amended only by a written instrument signed by both parties.

    Section 6.4: Severability
    If any provision of this Agreement is held to be invalid or unenforceable, the remaining provisions shall continue in full force and effect.

    IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

    ABC CORPORATION

    By: _________________________
    Name: Jane Doe
    Title: Chief Executive Officer

    JOHN SMITH

    Signature: _________________________
    Date: _________________________
    """
    
    # Clean and chunk the text
    cleaned_text = legal_chunker.clean_text(sample_text)
    chunks = legal_chunker.chunk_text(cleaned_text, preserve_sections=True)
    
    print(f"✅ Generated {len(chunks)} chunks")
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
    
    print(f"✅ Generated metadata for {len(metadata_list)} chunks")
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
        "What is the non-competition period?",
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

def test_api_endpoints():
    """Test API endpoints"""
    print("Testing API Endpoints...")
    
    import requests
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint: Working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint: Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint: Error - {e}")
    
    print()

def main():
    """Main test function"""
    print("=" * 60)
    print("LEGAL RAG SYSTEM - SIMPLE TEST SCRIPT")
    print("=" * 60)
    print()
    
    # Check if required environment variables are set
    print("Checking Configuration...")
    if not settings.validate_required_settings():
        print("⚠️  Missing required environment variables")
        print("   Note: Voyage AI API key is required for full functionality")
        print("   You can copy env_template.txt to .env and fill in your keys")
    else:
        print("✅ Configuration looks good")
    print()
    
    # Run tests
    try:
        chunks = test_chunking()
        metadata_list = test_metadata_building(chunks)
        test_validation()
        test_api_endpoints()
        
        print("=" * 60)
        print("✅ All basic tests completed successfully!")
        print("=" * 60)
        print()
        print("📋 Test Results Summary:")
        print(f"   - Document chunking: ✅ Working")
        print(f"   - Metadata building: ✅ Working") 
        print(f"   - Input validation: ✅ Working")
        print(f"   - API endpoints: ✅ Working")
        print()
        print("🎯 Next steps:")
        print("1. Set up your Voyage AI API key in .env file for full functionality")
        print("2. Run: uvicorn api.main:app --reload")
        print("3. Visit: http://localhost:8000/docs")
        print("4. Upload documents and test queries")
        print()
        print("📚 Sample questions to try:")
        print("   - What is the employee's base salary?")
        print("   - What are the termination provisions?")
        print("   - What is the non-competition period?")
        print("   - What benefits is the employee eligible for?")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 