#!/usr/bin/env python3
"""
Test script to check if the server is running
"""
import requests
import time
import sys

def test_server():
    """Test if the server is running and accessible"""
    print("Testing server connection...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Server responded with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("SERVER CONNECTION TEST")
    print("=" * 50)
    
    # Wait a moment for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    if test_server():
        print("\n🎉 Server is working correctly!")
        print("\nYou can now access:")
        print("- API Documentation: http://localhost:8000/docs")
        print("- Health Check: http://localhost:8000/health")
        print("- Alternative Docs: http://localhost:8000/redoc")
    else:
        print("\n❌ Server test failed")
        print("Please check:")
        print("1. Is the server running?")
        print("2. Are there any error messages?")
        print("3. Is port 8000 available?")

if __name__ == "__main__":
    main() 