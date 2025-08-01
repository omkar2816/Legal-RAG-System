# 🚀 How to Run the Legal RAG Project (Fixed)

## ✅ **The Server is Already Running!**

Good news! The server is currently running and accessible. You can access it at:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 **How to Start the Server (When Not Running)**

### **Method 1: Using Python Module (Recommended)**
```bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### **Method 2: Using the Startup Script**
```bash
python start_server.py
```

### **Method 3: Using the Test Script**
```bash
python test_server.py
```

## ❌ **What NOT to Do**
Don't use these commands (they won't work):
```bash
# ❌ This will fail
uvicorn api.main:app --reload

# ❌ This will also fail
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🛠️ **Complete Setup Process**

### **Step 1: Install Dependencies**
```bash
pip install -r requirements_simple.txt
```

### **Step 2: Set Up Environment**
```bash
# Copy environment template
cp env_template.txt .env

# Edit .env file and add your API keys
# VOYAGE_API_KEY=your_actual_voyage_api_key
# PINECONE_API_KEY=your_actual_pinecone_api_key
```

### **Step 3: Test the Setup**
```bash
# Test Voyage AI integration
python test_voyage_integration.py

# Test functionality
python test_voyage_functionality.py
```

### **Step 4: Start the Server**
```bash
# Use this command (NOT uvicorn directly)
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### **Step 5: Test the Server**
```bash
# Test if server is running
python test_server.py
```

## 🌐 **Accessing the Application**

Once the server is running, open your browser and go to:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Alternative Docs**: http://localhost:8000/redoc

## 🔧 **Testing the API**

### **Upload a Document**
```bash
# Using Python requests
python -c "
import requests
files = {'file': open('data/legal_docs/sample_contract.txt', 'rb')}
data = {'doc_type': 'employment_agreement', 'doc_title': 'Sample Contract'}
response = requests.post('http://localhost:8000/ingest/upload', files=files, data=data)
print('Upload response:', response.json())
"
```

### **Ask a Question**
```bash
# Using Python requests
python -c "
import requests
response = requests.post('http://localhost:8000/query/ask?question=What%20is%20the%20employee%27s%20base%20salary?')
print('Query response:', response.json())
"
```

## 🐛 **Troubleshooting**

### **Issue 1: "uvicorn: command not found"**
**Solution**: Use `python -m uvicorn` instead of `uvicorn`

### **Issue 2: "Site can't be reached"**
**Solutions**:
1. Make sure server is running: `python test_server.py`
2. Check if port 8000 is available: `netstat -an | grep 8000`
3. Try different port: `python -m uvicorn api.main:app --reload --port 8001`

### **Issue 3: Import errors**
**Solution**: Install dependencies
```bash
pip install -r requirements_simple.txt
```

### **Issue 4: API key errors**
**Solution**: Set up your `.env` file
```bash
cp env_template.txt .env
# Edit .env and add your actual API keys
```

## 📊 **Current Status**

| Component | Status | Notes |
|-----------|--------|-------|
| Server | ✅ Running | Port 8000 |
| API Documentation | ✅ Accessible | http://localhost:8000/docs |
| Voyage AI | ✅ Working | Embeddings functional |
| File Upload | ✅ Ready | Test with sample documents |

## 🎯 **Quick Commands**

### **Start Server**
```bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### **Test Server**
```bash
python test_server.py
```

### **Test Voyage AI**
```bash
python test_voyage_integration.py
```

### **Stop Server**
Press `Ctrl+C` in the terminal where the server is running

## 🎉 **You're Ready!**

1. **Server is running** ✅
2. **API is accessible** ✅
3. **Documentation available** ✅
4. **Ready to upload documents** ✅
5. **Ready to ask questions** ✅

**Open your browser and go to: http://localhost:8000/docs**

---

**The project is now running successfully! 🚀** 