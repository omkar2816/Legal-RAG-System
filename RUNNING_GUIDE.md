# 🚀 Legal RAG System - Running Guide

## 📋 Prerequisites

### 1. Python Environment
- Python 3.8 or higher (✅ You have Python 3.13.3)
- pip package manager

### 2. API Keys Required
- **Voyage AI API Key**: Get from https://platform.voyageai.com/
- **Pinecone API Key**: Get from https://app.pinecone.io/

## 🛠️ Installation Steps

### Step 1: Clone/Download the Project
```bash
# If you haven't already
cd "HackRx 6.0"
```

### Step 2: Install Dependencies
```bash
# Install simplified requirements (recommended for Windows)
pip install -r requirements_simple.txt
```

### Step 3: Set Up Environment Variables
1. Copy the environment template:
```bash
cp env_template.txt .env
```

2. Edit the `.env` file and add your API keys:
```env
# Voyage AI Configuration
VOYAGE_API_KEY=your_actual_voyage_api_key_here
VOYAGE_EMBEDDING_MODEL=voyage-large-2
VOYAGE_CHAT_MODEL=voyage-large-2

# Pinecone Configuration
PINECONE_API_KEY=your_actual_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
PINECONE_INDEX_NAME=legal-documents
```

### Step 4: Verify Installation
```bash
# Test Voyage AI integration
python test_voyage_integration.py

# Test functionality
python test_voyage_functionality.py
```

## 🚀 Running the Application

### Method 1: Using uvicorn (Recommended)
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Method 2: Using Python directly
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Method 3: Using the setup script
```bash
python setup.py
# Then start the server manually
```

## 🌐 Accessing the Application

Once the server is running, you can access:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Alternative API Docs**: http://localhost:8000/redoc

## 📁 Sample Data

The system includes sample legal documents:
- `data/legal_docs/sample_contract.txt` - Employment agreement
- `data/legal_docs/sample_nda.txt` - Non-disclosure agreement

## 🔧 Testing the System

### 1. Upload Documents
```bash
# Using curl
curl -X POST "http://localhost:8000/ingest/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/legal_docs/sample_contract.txt" \
  -F "doc_type=employment_agreement" \
  -F "doc_title=Sample Employment Contract"
```

### 2. Ask Questions
```bash
# Using curl
curl -X POST "http://localhost:8000/query/ask?question=What%20is%20the%20employee%27s%20base%20salary?"
```

### 3. Using the Web Interface
1. Go to http://localhost:8000/docs
2. Use the `/ingest/upload` endpoint to upload documents
3. Use the `/query/ask` endpoint to ask questions

## ⚠️ Important Notes

### Voyage AI Limitations
- **Embeddings**: ✅ Fully supported and working
- **LLM Completions**: ❌ Not supported in Python client (as of 2024)
- **Workaround**: Use HTTP API directly or another provider for chat/completions

### Sample Questions to Try
- "What is the employee's base salary?"
- "What are the termination provisions?"
- "What is the non-competition period?"
- "What are the confidentiality obligations?"

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Check what's using port 8000
netstat -an | grep 8000
# Use a different port
uvicorn api.main:app --reload --port 8001
```

2. **API Key Issues**
```bash
# Test your API keys
python test_voyage_integration.py
```

3. **Dependencies Issues**
```bash
# Reinstall dependencies
pip install -r requirements_simple.txt --force-reinstall
```

4. **Environment Variables**
```bash
# Check if .env file exists
ls -la .env
# Verify environment variables are loaded
python -c "from config.settings import settings; print('VOYAGE_API_KEY:', 'SET' if settings.VOYAGE_API_KEY else 'NOT SET')"
```

### Logs
Check the application logs:
```bash
tail -f legal_rag.log
```

## 📊 System Status

### ✅ Working Components
- Voyage AI embeddings
- Document processing
- Vector storage (Pinecone)
- Web API interface
- File upload functionality

### ⚠️ Limited Components
- LLM chat/completions (Voyage AI Python client limitation)

### 🔧 Configuration Options

Key settings in `config/settings.py`:
- `CHUNK_SIZE`: Text chunk size (default: 1000 words)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200 words)
- `TOP_K_RESULTS`: Number of search results (default: 5)
- `SEARCH_SIMILARITY_THRESHOLD`: Similarity threshold (default: 0.7)

## 🎯 Next Steps

1. **Set up your API keys** in the `.env` file
2. **Start the server** using one of the methods above
3. **Upload sample documents** using the web interface
4. **Test queries** to verify everything works
5. **Customize** the system for your specific needs

## 📞 Support

If you encounter issues:
1. Check the logs in `legal_rag.log`
2. Run the test scripts: `python test_voyage_integration.py`
3. Verify your API keys are correct
4. Check the API documentation at `/docs`

---

**Happy coding! 🎉** 