# Document Upload Guide - Legal RAG System

## 🎯 Overview

This guide shows you how to upload documents to your Legal RAG System, which automatically processes them and stores embeddings in Pinecone for semantic search.

## 📤 Upload Methods

### 1. **API Upload (Recommended)**

#### Single Document Upload
```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/document.pdf" \
  -F "doc_type=employment_agreement" \
  -F "doc_title=My Employment Contract"
```

#### Multiple Documents Upload
```bash
curl -X POST "http://localhost:8000/ingest/upload-multiple" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf" \
  -F "doc_types=employment_agreement,nda" \
  -F "doc_titles=Employment Contract,Non-Disclosure Agreement"
```

### 2. **Web Interface Upload**

1. Open your browser and go to: **http://localhost:8000/docs**
2. Find the `/ingest/upload` endpoint
3. Click "Try it out"
4. Upload your file and fill in the metadata
5. Click "Execute"

### 3. **Python Script Upload**

```python
import requests

# Upload a document
url = "http://localhost:8000/ingest/upload"
files = {
    'file': open('path/to/document.pdf', 'rb')
}
data = {
    'doc_type': 'employment_agreement',
    'doc_title': 'My Employment Contract'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## 📋 Supported File Types

- **PDF** (.pdf) - Text extraction and OCR
- **DOCX** (.docx) - Microsoft Word documents
- **TXT** (.txt) - Plain text files
- **Images** (.png, .jpg, .jpeg) - OCR processing

## 🏷️ Document Metadata

### Required Fields
- `file` - The document file to upload
- `doc_type` - Type of legal document (e.g., employment_agreement, nda, contract)
- `doc_title` - Human-readable title for the document

### Optional Fields
- `author` - Document author
- `date` - Document date
- `description` - Document description
- `tags` - Comma-separated tags

## 🔄 Upload Process

When you upload a document, the system:

1. **Validates** the file type and size
2. **Extracts** text from the document
3. **Cleans** and preprocesses the text
4. **Chunks** the text into semantic segments
5. **Generates** embeddings for each chunk
6. **Stores** vectors in Pinecone with metadata
7. **Returns** upload confirmation

## 📊 Monitoring Uploads

### Check Upload Status
```bash
curl -X GET "http://localhost:8000/ingest/status/{doc_id}"
```

### View System Statistics
```bash
curl -X GET "http://localhost:8000/admin/stats"
```

### Check Pinecone Index
```bash
python -c "
from vectordb.pinecone_client import get_index_stats
stats = get_index_stats()
print('Total vectors:', stats.get('total_vector_count', 0))
print('Namespaces:', stats.get('namespaces', {}))
"
```

## 🧪 Sample Upload Commands

### Upload Employment Contract
```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/legal_docs/sample_contract.txt" \
  -F "doc_type=employment_agreement" \
  -F "doc_title=Sample Employment Contract"
```

### Upload NDA
```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/legal_docs/sample_nda.txt" \
  -F "doc_type=nda" \
  -F "doc_title=Sample Non-Disclosure Agreement"
```

### Upload Multiple Documents
```bash
curl -X POST "http://localhost:8000/ingest/upload-multiple" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@data/legal_docs/sample_contract.txt" \
  -F "files=@data/legal_docs/sample_nda.txt" \
  -F "doc_types=employment_agreement,nda" \
  -F "doc_titles=Employment Contract,Non-Disclosure Agreement"
```

## ✅ Expected Responses

### Successful Upload
```json
{
  "message": "Document uploaded successfully and processing started",
  "file_path": "uploads/sample_contract_20250731_021916_a145cc13.txt",
  "warnings": []
}
```

### Processing Status
```json
{
  "status": "completed",
  "doc_id": "sample_contract_001",
  "chunks_processed": 5,
  "embeddings_generated": 5,
  "vectors_stored": 5
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **File Too Large**
- Maximum file size: 50MB
- Solution: Compress or split large documents

#### 2. **Unsupported File Type**
- Supported: PDF, DOCX, TXT, PNG, JPG, JPEG
- Solution: Convert to supported format

#### 3. **OpenAI API Quota Exceeded**
- Symptoms: 429 errors in logs
- Solution: Add credits to OpenAI account or use different API key

#### 4. **Pinecone Connection Issues**
- Symptoms: Vector storage failures
- Solution: Check Pinecone API key and index configuration

### Debug Steps

1. **Check Logs**:
   ```bash
   tail -f legal_rag.log
   ```

2. **Verify API Health**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **Test File Validation**:
   ```bash
   curl -X POST "http://localhost:8000/ingest/validate" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf"
   ```

## 📈 Performance Tips

1. **Batch Uploads**: Use `/ingest/upload-multiple` for multiple files
2. **File Optimization**: Compress large PDFs before upload
3. **Metadata**: Provide detailed metadata for better search results
4. **Monitoring**: Check processing status for large documents

## 🎯 Next Steps After Upload

1. **Test Queries**: Ask questions about uploaded documents
2. **Monitor Performance**: Check response times and accuracy
3. **Scale Up**: Add more documents to improve search coverage
4. **Optimize**: Fine-tune chunking and embedding parameters

## 📞 Support

If you encounter issues:
1. Check the logs in `legal_rag.log`
2. Verify your API keys and billing
3. Test with sample documents first
4. Check the troubleshooting section above

Happy uploading! 🚀 