# Legal RAG System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Pinecone API key

### 2. Quick Setup
```bash
# Clone or download the project
cd legal-rag-system

# Run the setup script
python setup.py

# Or manually:
pip install -r requirements.txt
cp env_template.txt .env
# Edit .env with your API keys
```

### 3. Configure API Keys
Edit the `.env` file and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 4. Start the Application
```bash
uvicorn api.main:app --reload
```

### 5. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 Sample Usage

### Upload Documents
```bash
# Using curl
curl -X POST "http://localhost:8000/ingest/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/legal_docs/sample_contract.txt" \
  -F "doc_type=employment_agreement" \
  -F "doc_title=Sample Employment Contract"
```

### Ask Questions
```bash
# Using curl
curl -X POST "http://localhost:8000/query/ask?question=What%20is%20the%20employee%27s%20base%20salary?"
```

### Using the Web Interface
1. Go to http://localhost:8000/docs
2. Use the `/ingest/upload` endpoint to upload documents
3. Use the `/query/ask` endpoint to ask questions

## 📁 Sample Data

The system includes sample legal documents:
- `data/legal_docs/sample_contract.txt` - Employment agreement
- `data/legal_docs/sample_nda.txt` - Non-disclosure agreement

Sample questions to try:
- "What is the employee's base salary?"
- "What are the termination provisions?"
- "What is the non-competition period?"
- "What are the confidentiality obligations?"

## 🔧 Configuration

Key settings in `config/settings.py`:
- `CHUNK_SIZE`: Text chunk size (default: 1000 words)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200 words)
- `TOP_K_RESULTS`: Number of search results (default: 5)
- `SEARCH_SIMILARITY_THRESHOLD`: Similarity threshold (default: 0.7)

## 🧪 Testing

Run the test script to verify everything works:
```bash
python test_system.py
```

## 📊 API Endpoints

### Document Ingestion
- `POST /ingest/upload` - Upload single document
- `POST /ingest/upload-multiple` - Upload multiple documents
- `GET /ingest/status/{doc_id}` - Check processing status

### Query Interface
- `POST /query/ask` - Ask legal questions
- `GET /query/search` - Search documents
- `GET /query/suggest` - Get suggested questions

### Administration
- `GET /admin/health` - Health check
- `GET /admin/stats` - System statistics
- `DELETE /admin/documents/{doc_id}` - Delete document
- `POST /admin/cleanup` - System cleanup

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure `.env` file exists and contains valid API keys
   - Check that keys are not expired

2. **Pinecone Connection Issues**
   - Verify Pinecone API key and environment
   - Check if index exists in your Pinecone account

3. **OpenAI API Errors**
   - Verify OpenAI API key
   - Check API usage limits and billing

4. **File Upload Issues**
   - Ensure file size is under 50MB
   - Check file format is supported (PDF, TXT, DOCX, images)

### Logs
Check the application logs:
```bash
tail -f legal_rag.log
```

## 📈 Performance Tips

1. **Chunk Size**: Adjust `CHUNK_SIZE` based on your documents
2. **Batch Processing**: Use `/ingest/upload-multiple` for multiple files
3. **Caching**: Consider adding Redis for response caching
4. **Indexing**: Monitor Pinecone index performance

## 🔒 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **File Validation**: All uploaded files are validated
3. **Rate Limiting**: Implement rate limiting for production
4. **CORS**: Configure CORS appropriately for your domain

## 📞 Support

For issues and questions:
1. Check the logs in `legal_rag.log`
2. Review the API documentation at `/docs`
3. Run the test script: `python test_system.py`

## 🎯 Next Steps

1. **Production Deployment**: Use Docker and proper web server
2. **Authentication**: Add user authentication and authorization
3. **Database**: Add persistent storage for document metadata
4. **Monitoring**: Add application monitoring and alerting
5. **Scaling**: Consider horizontal scaling for high traffic 