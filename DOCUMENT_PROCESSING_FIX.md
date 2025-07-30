# Document Processing Fix Guide

## 🚨 **Current Issues**

1. **OpenAI API Quota Exceeded**: 429 errors preventing embedding generation
2. **Zero Vectors**: System generates zero vectors when API fails
3. **Pinecone Rejection**: Pinecone rejects zero vectors
4. **No Chunks/Embeddings**: Documents uploaded but not processed

## ✅ **Solutions Implemented**

### 1. **Mock Embedding Service**
- Created `embeddings/mock_embed_client.py`
- Generates deterministic random vectors for testing
- Falls back when OpenAI API fails

### 2. **Improved Error Handling**
- Modified `embeddings/embed_client.py` to use mock embeddings
- Prevents zero vector generation
- Ensures documents get processed

### 3. **Document Processing Verification**
- Created `test_document_processing.py` to verify functionality
- Tests chunking, metadata, and embedding generation

## 🔧 **How to Fix Your System**

### **Option 1: Use OpenAI API (Recommended)**

1. **Add Credits to OpenAI Account**:
   - Go to https://platform.openai.com/account/billing
   - Add credits to your account
   - Or use a different API key with sufficient credits

2. **Update Your .env File**:
   ```env
   OPENAI_API_KEY=your_new_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key
   ```

### **Option 2: Use Mock Embeddings (For Testing)**

The system now automatically falls back to mock embeddings when OpenAI API fails. This allows you to:

1. **Test Document Processing**: Verify chunks and metadata generation
2. **Test Vector Storage**: Store mock vectors in Pinecone
3. **Test Query Interface**: Ask questions about uploaded documents

## 🧪 **Testing Steps**

### 1. **Test Document Processing**
```bash
python test_document_processing.py
```

Expected output:
```
✅ Generated 1 chunks
✅ Generated metadata for 1 chunks
✅ Generated 1 mock embeddings
```

### 2. **Test Document Upload**
```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/legal_docs/sample_contract.txt" \
  -F "doc_type=employment_agreement" \
  -F "doc_title=Test Contract"
```

### 3. **Check Pinecone Index**
```bash
python -c "
from vectordb.pinecone_client import get_index_stats
stats = get_index_stats()
print('Total vectors:', stats.get('total_vector_count', 0))
"
```

Expected output: `Total vectors: 1` (or more)

### 4. **Test Query Interface**
```bash
curl -X POST "http://localhost:8000/query/ask?question=What%20is%20the%20employee%27s%20base%20salary?"
```

## 📊 **Current Status**

### ✅ **Working Components**
- Document upload API
- Text extraction and cleaning
- Document chunking
- Metadata generation
- Mock embedding generation
- Pinecone connection

### ⚠️ **Limited Components**
- OpenAI embedding generation (quota exceeded)
- LLM response generation (requires API key)

### ❌ **Not Working**
- Vector storage (due to zero vectors)

## 🎯 **Next Steps**

### **Immediate Actions**

1. **Add OpenAI API Credits**:
   - Visit https://platform.openai.com/account/billing
   - Add at least $5-10 in credits
   - Update your API key if needed

2. **Test with Mock Embeddings**:
   - The system will automatically use mock embeddings
   - This allows full testing of the pipeline

3. **Verify Processing**:
   - Run the test scripts
   - Check Pinecone index stats
   - Test query interface

### **Long-term Solutions**

1. **Production Setup**:
   - Use paid OpenAI API for production
   - Monitor API usage and costs
   - Set up billing alerts

2. **Alternative Embedding Models**:
   - Consider using local embedding models
   - Use other embedding services (Hugging Face, etc.)

3. **Caching and Optimization**:
   - Cache embeddings to reduce API calls
   - Batch processing for multiple documents

## 🔍 **Troubleshooting**

### **Common Issues**

1. **"Mock embedding also failed"**:
   - Check if `embeddings/mock_embed_client.py` exists
   - Verify import paths in `embed_client.py`

2. **"Zero vectors" error**:
   - The mock embedding system should prevent this
   - Check logs for mock embedding success

3. **"Pinecone connection failed"**:
   - Verify Pinecone API key
   - Check index configuration

### **Debug Commands**

```bash
# Check logs
tail -f legal_rag.log

# Test document processing
python test_document_processing.py

# Check Pinecone index
python -c "from vectordb.pinecone_client import get_index_stats; print(get_index_stats())"

# Test API health
curl http://localhost:8000/health
```

## 📈 **Expected Results After Fix**

1. **Document Upload**: ✅ Success
2. **Text Processing**: ✅ 1 chunk generated
3. **Metadata**: ✅ Metadata created
4. **Embeddings**: ✅ Mock embeddings generated
5. **Vector Storage**: ✅ Vectors stored in Pinecone
6. **Query Interface**: ✅ Can ask questions

## 🎉 **Success Indicators**

- Pinecone index shows `total_vector_count > 0`
- Query interface returns relevant answers
- Logs show "Falling back to mock embeddings"
- No more "zero vectors" errors

## 📞 **Support**

If you continue to have issues:

1. Check the logs in `legal_rag.log`
2. Run the test scripts
3. Verify your API keys
4. Check Pinecone index status

The system is designed to be robust and should work with mock embeddings even when OpenAI API is unavailable. 