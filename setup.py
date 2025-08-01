#!/usr/bin/env python3
"""
Setup script for the Legal RAG System
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_env_file():
    """Create .env file from template"""
    print("📝 Creating .env file...")
    env_template = Path("env_template.txt")
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists, skipping creation")
        return True
    
    if env_template.exists():
        # Copy template to .env
        with open(env_template, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created from template")
        print("⚠️  Please edit .env file and add your API keys")
        return True
    else:
        print("❌ env_template.txt not found")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "uploads",
        "processed",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    return run_command("python test_system.py", "Running system tests")

def main():
    """Main setup function"""
    print("=" * 60)
    print("LEGAL RAG SYSTEM - SETUP SCRIPT")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        print("You may need to set up your API keys first")
    
    print()
    print("=" * 60)
    print("🎉 SETUP COMPLETED!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Edit .env file and add your API keys:")
    print("   - VOYAGE_API_KEY: Get from https://platform.voyageai.com/")
    print("   - PINECONE_API_KEY: Get from https://app.pinecone.io/")
    print()
    print("2. Start the application:")
    print("   uvicorn api.main:app --reload")
    print()
    print("3. Access the API documentation:")
    print("   http://localhost:8000/docs")
    print()
    print("4. Upload sample documents and test queries!")
    print()
    print("Sample documents are available in data/legal_docs/")
    print("Sample queries are available in data/sample_queries.txt")

if __name__ == "__main__":
    main() 