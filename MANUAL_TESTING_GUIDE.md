# 📋 Manual Testing Guide - Legal RAG System

## 🎯 **How to Test Document Upload Manually**

### **Step 1: Start the Server**
```bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### **Step 2: Access the Web Interface**
Open your browser and go to: **http://localhost:8000/docs**

You'll see the FastAPI Swagger UI with all available endpoints.

---

## 🔧 **Method 1: Using the Web Interface (Recommended)**

### **1. Upload a Document**
1. **Find the Upload Endpoint**: Look for `POST /ingest/upload` in the Swagger UI
2. **Click "Try it out"**
3. **Fill in the form**:
   - **file**: Click "Choose File" and select a document (e.g., `data/legal_docs/sample_contract.txt`)
   - **doc_type**: Enter `employment_agreement` (or any type)
   - **doc_title**: Enter `Sample Employment Contract`
   - **doc_author**: Enter `Legal Team`
4. **Click "Execute"**
5. **Check the Response**: You should see:
   ```json
   {
     "message": "Document uploaded successfully and processing started",
     "file_path": "uploads/sample_contract_20250801_xxxxx.txt",
     "warnings": []
   }
   ```

### **2. Check System Status**
1. **Find the Stats Endpoint**: Look for `GET /admin/stats`
2. **Click "Try it out"**
3. **Click "Execute"**
4. **Check the Response**: You should see system statistics including Pinecone index info

### **3. Ask Questions**
1. **Find the Query Endpoint**: Look for `POST /query/ask`
2. **Click "Try it out"**
3. **Enter a question**: `What is the employee's base salary?`
4. **Click "Execute"**
5. **Check the Response**: You should see an answer based on the uploaded documents

---

## 🔧 **Method 2: Using curl Commands**

### **1. Upload a Document**
```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/legal_docs/sample_contract.txt" \
  -F "doc_type=employment_agreement" \
  -F "doc_title=Sample Employment Contract" \
  -F "doc_author=Legal Team"
```

### **2. Check System Stats**
```bash
curl -X GET "http://localhost:8000/admin/stats"
```

### **3. Ask a Question**
```bash
curl -X POST "http://localhost:8000/query/ask?question=What%20is%20the%20employee%27s%20base%20salary?"
```

---

## 🔧 **Method 3: Using Python Scripts**

### **1. Upload Test Script**
```python
import requests

# Upload a document
with open('data/legal_docs/sample_contract.txt', 'rb') as f:
    files = {'file': f}
    data = {
        'doc_type': 'employment_agreement',
        'doc_title': 'Sample Employment Contract',
        'doc_author': 'Legal Team'
    }
    
    response = requests.post('http://localhost:8000/ingest/upload', files=files, data=data)
    print(f"Upload Status: {response.status_code}")
    print(f"Response: {response.json()}")
```

### **2. Query Test Script**
```python
import requests

# Ask a question
response = requests.post('http://localhost:8000/query/ask?question=What%20is%20the%20employee%27s%20base%20salary?')
print(f"Query Status: {response.status_code}")
print(f"Answer: {response.json()}")
```

---

## 📊 **What to Look For**

### **✅ Successful Upload**
- Status code: `202`
- Response includes file path
- No error messages

### **✅ Successful Processing**
- Check system stats shows vectors in Pinecone
- `total_vector_count` should increase
- Processed files should appear in stats

### **✅ Successful Query**
- Status code: `200`
- Response includes relevant answer
- Sources should be listed

---

## 🐛 **Troubleshooting**

### **Issue 1: Upload Fails**
- **Check**: File size and type
- **Solution**: Use smaller files or check file format

### **Issue 2: Processing Fails**
- **Check**: Server logs for errors
- **Solution**: Verify API keys are set correctly

### **Issue 3: No Query Results**
- **Check**: System stats for vector count
- **Solution**: Wait for processing to complete

### **Issue 4: Server Not Starting**
- **Check**: Port 8000 availability
- **Solution**: Use different port: `--port 8001`

---

## 📁 **Sample Documents to Test**

### **Available Sample Files**
- `data/legal_docs/sample_contract.txt` - Employment agreement
- `data/legal_docs/sample_nda.txt` - Non-disclosure agreement

### **Sample Questions to Try**
1. "What is the employee's base salary?"
2. "What are the termination provisions?"
3. "What is the non-competition period?"
4. "What are the confidentiality obligations?"

---

## 🎯 **Step-by-Step Testing Process**

### **Phase 1: Basic Upload**
1. Start server
2. Upload sample contract
3. Check upload response
4. Wait 10-15 seconds for processing

### **Phase 2: Verify Processing**
1. Check system stats
2. Look for vector count increase
3. Verify processed files list

### **Phase 3: Test Queries**
1. Ask basic questions
2. Check response quality
3. Verify source citations

### **Phase 4: Test Multiple Documents**
1. Upload NDA document
2. Ask questions about both documents
3. Verify cross-document search

---

## 📈 **Expected Results**

### **After Upload**
```json
{
  "message": "Document uploaded successfully and processing started",
  "file_path": "uploads/sample_contract_20250801_xxxxx.txt",
  "warnings": []
}
```

### **After Processing**
```json
{
  "index_stats": {
    "total_vector_count": 15,
    "dimension": 1024
  },
  "processed_files": {
    "count": 1,
    "files": ["sample_contract_20250801_xxxxx.txt"]
  }
}
```

### **After Query**
```json
{
  "answer": "Based on the employment contract, the employee's base salary is $120,000 per year...",
  "sources": ["sample_contract_20250801_xxxxx.txt"],
  "confidence": 0.85
}
```

---

## 🎉 **Success Criteria**

✅ **Upload**: File accepted with status 202  
✅ **Processing**: Vectors stored in Pinecone  
✅ **Query**: Relevant answers returned  
✅ **Sources**: Document citations provided  
✅ **Performance**: Response time under 5 seconds  

---

**Happy Testing! 🚀** 