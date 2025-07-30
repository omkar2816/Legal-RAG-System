#!/usr/bin/env python3
"""
Document Upload Script for Legal RAG System
This script demonstrates how to upload documents programmatically
"""
import requests
import os
from pathlib import Path

def upload_single_document(file_path, doc_type, doc_title, api_url="http://localhost:8000"):
    """
    Upload a single document to the Legal RAG System
    
    Args:
        file_path: Path to the document file
        doc_type: Type of legal document
        doc_title: Human-readable title
        api_url: API base URL
    
    Returns:
        Response from the API
    """
    url = f"{api_url}/ingest/upload"
    
    with open(file_path, 'rb') as file:
        files = {'file': file}
        data = {
            'doc_type': doc_type,
            'doc_title': doc_title
        }
        
        response = requests.post(url, files=files, data=data)
        return response.json()

def upload_multiple_documents(file_paths, doc_types, doc_titles, api_url="http://localhost:8000"):
    """
    Upload multiple documents to the Legal RAG System
    
    Args:
        file_paths: List of file paths
        doc_types: List of document types
        doc_titles: List of document titles
        api_url: API base URL
    
    Returns:
        Response from the API
    """
    url = f"{api_url}/ingest/upload-multiple"
    
    files = []
    for file_path in file_paths:
        files.append(('files', open(file_path, 'rb')))
    
    data = {
        'doc_types': ','.join(doc_types),
        'doc_titles': ','.join(doc_titles)
    }
    
    response = requests.post(url, files=files, data=data)
    
    # Close all files
    for _, file in files:
        file.close()
    
    return response.json()

def check_upload_status(doc_id, api_url="http://localhost:8000"):
    """
    Check the status of a document upload
    
    Args:
        doc_id: Document ID
        api_url: API base URL
    
    Returns:
        Status response
    """
    url = f"{api_url}/ingest/status/{doc_id}"
    response = requests.get(url)
    return response.json()

def get_system_stats(api_url="http://localhost:8000"):
    """
    Get system statistics
    
    Args:
        api_url: API base URL
    
    Returns:
        System stats
    """
    url = f"{api_url}/admin/stats"
    response = requests.get(url)
    return response.json()

def main():
    """Main function to demonstrate document uploads"""
    print("=" * 60)
    print("LEGAL RAG SYSTEM - DOCUMENT UPLOAD DEMO")
    print("=" * 60)
    
    # Check if server is running
    try:
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    print()
    
    # Sample documents
    sample_docs = [
        {
            'path': 'data/legal_docs/sample_contract.txt',
            'type': 'employment_agreement',
            'title': 'Sample Employment Contract'
        },
        {
            'path': 'data/legal_docs/sample_nda.txt',
            'type': 'nda',
            'title': 'Sample Non-Disclosure Agreement'
        }
    ]
    
    # Upload documents one by one
    print("📤 Uploading documents individually...")
    for doc in sample_docs:
        if os.path.exists(doc['path']):
            print(f"Uploading: {doc['title']}")
            try:
                result = upload_single_document(
                    doc['path'], 
                    doc['type'], 
                    doc['title']
                )
                print(f"✅ Success: {result.get('message', 'Uploaded')}")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print(f"⚠️  File not found: {doc['path']}")
    
    print()
    
    # Upload multiple documents at once
    print("📤 Uploading multiple documents...")
    file_paths = [doc['path'] for doc in sample_docs if os.path.exists(doc['path'])]
    doc_types = [doc['type'] for doc in sample_docs if os.path.exists(doc['path'])]
    doc_titles = [doc['title'] for doc in sample_docs if os.path.exists(doc['path'])]
    
    if file_paths:
        try:
            result = upload_multiple_documents(file_paths, doc_types, doc_titles)
            print("✅ Multiple upload result:")
            for item in result.get('results', []):
                print(f"  - {item['filename']}: {item['status']}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()
    
    # Get system statistics
    print("📊 System Statistics:")
    try:
        stats = get_system_stats()
        print(f"  - Documents processed: {stats.get('documents_processed', 0)}")
        print(f"  - Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  - Embeddings generated: {stats.get('embeddings_generated', 0)}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    print()
    print("🎯 Next steps:")
    print("1. Check the logs: tail -f legal_rag.log")
    print("2. Test queries: curl -X POST 'http://localhost:8000/query/ask?question=What%20is%20the%20employee%27s%20salary?'")
    print("3. Visit the web interface: http://localhost:8000/docs")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main() 