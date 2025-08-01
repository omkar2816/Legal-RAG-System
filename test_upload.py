#!/usr/bin/env python3
"""
Test script to upload a document and check the results
"""
import requests
import time

def test_upload():
    """Test document upload"""
    print("Testing document upload...")
    
    try:
        # Upload the sample NDA document
        with open('data/legal_docs/sample_nda.txt', 'rb') as f:
            files = {'file': f}
            data = {
                'doc_type': 'nda',
                'doc_title': 'Sample NDA',
                'doc_author': 'Legal Team'
            }
            
            print("Uploading sample NDA document...")
            response = requests.post('http://localhost:8000/ingest/upload', files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 202:
                print("✅ Upload successful!")
                
                # Wait a moment for processing
                print("Waiting for processing to complete...")
                time.sleep(5)
                
                # Check system stats
                print("\nChecking system stats...")
                stats_response = requests.get('http://localhost:8000/admin/stats')
                print(f"Stats Status: {stats_response.status_code}")
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    print("✅ System stats retrieved successfully!")
                    print(f"Stats: {stats}")
                else:
                    print(f"❌ Stats error: {stats_response.text}")
            else:
                print("❌ Upload failed!")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_upload() 