#!/usr/bin/env python3
"""
Startup script for the Legal RAG System
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create .env file from env_template.txt:")
        print("cp env_template.txt .env")
        print("Then edit .env and add your API keys")
        return False
    
    # Check for required API keys
    with open(env_file, 'r') as f:
        content = f.read()
    
    required_keys = ["VOYAGE_API_KEY", "PINECONE_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if key not in content or f"{key}=" in content and "your_" in content:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing or invalid API keys: {', '.join(missing_keys)}")
        print("Please edit .env file and add your actual API keys")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from api.main import app
        print("✅ App imports successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def start_server():
    """Start the uvicorn server"""
    print("🚀 Starting Legal RAG Server...")
    print("=" * 50)
    
    # Check environment
    if not check_env_file():
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    # Get host and port from environment variables or use defaults
    # Always use 0.0.0.0 as host on Render to ensure proper port binding
    host = "0.0.0.0"
    port = int(os.getenv("PORT", "8000"))
    
    print(f"\n🌐 Server will be available at:")
    print(f"   - API Documentation: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    print(f"   - Health Check: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/health")
    print(f"   - Alternative Docs: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/redoc")
    print("\n📁 Sample documents available in data/legal_docs/")
    print("🔧 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start uvicorn server
        # Always use 0.0.0.0 as host on Render to ensure proper port binding
        cmd = [
            sys.executable, "-m", "uvicorn",
            "api.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", str(port)
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("=" * 60)
    print("LEGAL RAG SYSTEM - SERVER STARTUP")
    print("=" * 60)
    print()
    
    if start_server():
        print("\n✅ Server started successfully!")
    else:
        print("\n❌ Failed to start server")
        sys.exit(1)

if __name__ == "__main__":
    main()