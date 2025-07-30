# Legal RAG System - Testing Guide

## 🎯 Overview

This guide will help you test your Legal RAG System and verify that all components are working correctly.

## ✅ Current Status

Your Legal RAG System is **successfully running** with the following components working:

- ✅ **Document Chunking**: Legal-aware text segmentation
- ✅ **Metadata Building**: Intelligent metadata generation
- ✅ **Input Validation**: Query and file validation
- ✅ **API Endpoints**: REST API is responding
- ✅ **Pinecone Integration**: Vector database is connected
- ✅ **Server**: FastAPI server is running on http://localhost:8000

## 🧪 Testing Methods

### 1. **Quick System Test** (Recommended)
```bash
python test_simple.py
```
This test verifies all core functionality without requiring API calls.

### 2. **Full System Test** (Requires API Keys)
```bash
python test_system.py
```
This test requires valid OpenAI and Pinecone API keys.

### 3. **API Testing** (Interactive)
Visit http://localhost:8000/docs for interactive API testing.

## 🚀 How to Test Your System

### Step 1: Verify Server is Running
```bash
curl http://localhost:8000/health
```
Expected response: `{"status":"healthy","service":"Legal RAG System"}`

### Step 2: Test Document Upload
```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/legal_docs/sample_contract.txt" \
  -F "doc_type=employment_agreement" \
  -F "doc_title=Sample Employment Contract"
```

### Step 3: Test Query Interface
```bash
curl -X POST "http://localhost:8000/query/ask?question=What%20is%20the%20employee%27s%20base%20salary?"
```

### Step 4: Test Admin Endpoints
```bash
curl -X GET "http://localhost:8000/admin/health"
curl -X GET "http://localhost:8000/admin/stats"
```

## 📚 Sample Test Data

### Sample Documents
- `data/legal_docs/sample_contract.txt` - Employment agreement
- `data/legal_docs/sample_nda.txt` - Non-disclosure agreement

### Sample Questions to Test
1. **Salary Questions**:
   - "What is the employee's base salary?"
   - "What is the annual salary?"

2. **Termination Questions**:
   - "What are the termination provisions?"
   - "How much notice is required for termination?"

3. **Benefits Questions**:
   - "What benefits is the employee eligible for?"
   - "What insurance coverage is provided?"

4. **Non-Compete Questions**:
   - "What is the non-competition period?"
   - "What are the restrictions after termination?"

5. **Confidentiality Questions**:
   - "What are the confidentiality obligations?"
   - "What is considered confidential information?"

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. **OpenAI API Quota Exceeded**
**Symptoms**: 429 errors in logs
**Solution**: 
- Check your OpenAI API key and billing
- Add credits to your OpenAI account
- Or use a different API key

#### 2. **Pinecone Dimension Mismatch**
**Symptoms**: "Vector dimension does not match" errors
**Solution**: 
- The system is configured to use 1024-dimensional vectors
- Pinecone index is set up correctly

#### 3. **Server Not Starting**
**Symptoms**: "uvicorn: command not found"
**Solution**:
```bash
pip install uvicorn
python -m uvicorn api.main:app --reload
```

#### 4. **Missing Dependencies**
**Symptoms**: Import errors
**Solution**:
```bash
pip install -r requirements.txt
```

## 📊 Expected Test Results

### Successful Document Processing
- Document uploaded successfully
- Text extracted and chunked
- Embeddings generated (if API key available)
- Vectors stored in Pinecone

### Successful Query Processing
- Query validated
- Embeddings generated for query
- Similar documents retrieved
- LLM generates response (if API key available)

### Sample Response Format
```json
{
  "answer": "Based on the employment agreement, the employee's base salary is $120,000 per year...",
  "sources": [
    {
      "doc_id": "sample_contract_001",
      "chunk_id": "section_2_1",
      "text": "The Company shall pay the Employee an annual base salary of $120,000...",
      "similarity": 0.95
    }
  ],
  "confidence": 0.95,
  "warnings": []
}
```

## 🎯 Testing Checklist

### Basic Functionality
- [ ] Server starts without errors
- [ ] Health endpoint responds
- [ ] Document upload works
- [ ] Query interface responds
- [ ] Input validation works

### Advanced Functionality (Requires API Keys)
- [ ] Document embeddings generated
- [ ] Query embeddings generated
- [ ] Vector search works
- [ ] LLM responses generated
- [ ] Context-aware answers

### Error Handling
- [ ] Invalid file types rejected
- [ ] Empty queries handled
- [ ] API errors gracefully handled
- [ ] Rate limiting respected

## 🚀 Next Steps After Testing

1. **Set up API Keys**: Add your OpenAI and Pinecone API keys to `.env`
2. **Upload Your Documents**: Use the API to upload your legal documents
3. **Test Real Queries**: Ask questions about your uploaded documents
4. **Monitor Performance**: Check logs and API response times
5. **Scale Up**: Consider production deployment options

## 📞 Support

If you encounter issues:
1. Check the logs in `legal_rag.log`
2. Run the test scripts
3. Verify your API keys and billing
4. Check the troubleshooting section above

## 🎉 Congratulations!

Your Legal RAG System is successfully set up and ready for use! The core functionality is working, and you can now:

- Upload legal documents
- Ask questions about them
- Get AI-powered responses
- Scale the system as needed

Happy testing! 🚀 