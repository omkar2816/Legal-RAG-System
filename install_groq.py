#!/usr/bin/env python3
"""
Installation script for Groq integration
"""
import subprocess
import sys
import os

def install_groq():
    """Install Groq dependency"""
    print("Installing Groq dependency...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "groq>=0.4.2"])
        print("✅ Groq dependency installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Groq: {e}")
        return False

def check_environment():
    """Check if environment variables are set"""
    print("Checking environment variables...")
    
    required_vars = ["VOYAGE_API_KEY", "GROQ_API_KEY", "PINECONE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please add these to your .env file:")
        for var in missing_vars:
            if var == "GROQ_API_KEY":
                print(f"  {var}=your_groq_api_key_here")
            elif var == "VOYAGE_API_KEY":
                print(f"  {var}=your_voyage_api_key_here")
            elif var == "PINECONE_API_KEY":
                print(f"  {var}=your_pinecone_api_key_here")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_import():
    """Test if Groq can be imported"""
    print("Testing Groq import...")
    try:
        import groq
        print("✅ Groq module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Groq: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 Groq Integration Installation")
    print("=" * 40)
    
    # Install Groq
    if not install_groq():
        sys.exit(1)
    
    # Test import
    if not test_import():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\n📝 Please set up your environment variables and run the test:")
        print("python test_groq_integration.py")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("You can now test the integration with:")
    print("python test_groq_integration.py")

if __name__ == "__main__":
    main() 