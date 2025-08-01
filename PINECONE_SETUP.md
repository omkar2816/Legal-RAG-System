# Pinecone Setup Guide for Legal RAG System

## 🎯 Overview

This guide will help you set up Pinecone for the Legal RAG System. Pinecone is used as the vector database to store and search document embeddings.

## 📋 Prerequisites

1. **Pinecone Account**: Sign up at https://app.pinecone.io/
2. **API Key**: Get your API key from the Pinecone console
3. **Environment**: Note your Pinecone environment (e.g., `us-east-1`, `us-west-1`)
4. **Credits**: Ensure you have sufficient credits for serverless index creation

## 🚀 Quick Setup

### Step 1: Get Your Pinecone API Key

1. Go to https://app.pinecone.io/
2. Sign up or log in to your account
3. Navigate to the API Keys section
4. Copy your API key

### Step 2: Configure Your Environment

1. **Create `.env` file** (if not already done):
   ```bash
   cp env_template.txt .env
   ```

2. **Edit `.env` file** and add your Pinecone credentials:
   ```env
   # Pinecone Configuration
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_ENVIRONMENT=us-east-1
   PINECONE_INDEX_NAME=legal-rag-index
   PINECONE_DIMENSION=1536
   ```

### Step 3: Create the Index

**Option A: Using the automated script (Recommended)**
```bash
python create_pinecone_index.py
```

**Option B: Manual creation**
```bash
python -c "from vectordb.pinecone_client import create_index; create_index()"
```

**Option C: Using Python directly**
```python
from pinecone import Pinecone, ServerlessSpec
from config.settings import settings

# Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# Create serverless index
pc.create_index(
    name=settings.PINECONE_INDEX_NAME,
    dimension=settings.PINECONE_DIMENSION,
    metric="cosine",
    spec=ServerlessSpec(
        cloud='aws',
        region=settings.PINECONE_ENVIRONMENT
    )
)
```

## ⚙️ Index Configuration Details

### Default Settings
- **Index Name**: `legal-rag-index`
- **Dimension**: `1024` (Voyage AI embedding dimension)
- **Metric**: `cosine` (similarity metric)
- **Type**: Serverless (AWS)
- **Region**: Based on your environment setting

### Customizable Settings
You can modify these in your `.env` file:

```env
# Change index name (optional)
PINECONE_INDEX_NAME=my-legal-index

# Change environment (use your Pinecone environment)
PINECONE_ENVIRONMENT=us-west-1

# Change dimension (if using different embedding model)
PINECONE_DIMENSION=1536
```

## 🔍 Verifying Your Setup

### Check Index Creation
```bash
python -c "
from vectordb.pinecone_client import get_index_stats
stats = get_index_stats()
print('Index Stats:', stats)
"
```

### Test the Application
```bash
# Start the application
uvicorn api.main:app --reload

# Check health endpoint
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid API Key" Error**
   - Verify your API key is correct
   - Check that the key is not expired
   - Ensure you copied the entire key

2. **"Environment Not Found" Error**
   - Verify your Pinecone environment
   - Common environments: `us-east-1`, `us-west-1`, `eu-west-1`
   - Check your Pinecone console for the correct environment

3. **"Index Already Exists" Error**
   - This is normal if the index was already created
   - The application will use the existing index

4. **"Permission Denied" Error**
   - Check your Pinecone account permissions
   - Ensure your account has index creation privileges

5. **"Insufficient Credits" Error**
   - Check your Pinecone account balance
   - Serverless indexes require credits to create and maintain

6. **"Index Still Initializing" Error**
   - New indexes take a few minutes to initialize
   - Wait 5-10 minutes and try again

### Debug Steps

1. **Test Pinecone Connection**:
   ```python
   from pinecone import Pinecone
   pc = Pinecone(api_key="your_key")
   print("Available indexes:", pc.list_indexes().names())
   ```

2. **Check Environment Variables**:
   ```python
   from config.settings import settings
   print("API Key:", settings.PINECONE_API_KEY[:10] + "...")
   print("Environment:", settings.PINECONE_ENVIRONMENT)
   print("Index Name:", settings.PINECONE_INDEX_NAME)
   ```

3. **Verify Index Creation**:
   ```python
   from pinecone import Pinecone
   from config.settings import settings
   
   pc = Pinecone(api_key=settings.PINECONE_API_KEY)
   indexes = pc.list_indexes().names()
   print(f"Index '{settings.PINECONE_INDEX_NAME}' exists: {settings.PINECONE_INDEX_NAME in indexes}")
   ```

## 📊 Index Management

### View Index Statistics
```python
from vectordb.pinecone_client import get_index_stats
stats = get_index_stats()
print(f"Total vectors: {stats.get('total_vector_count', 0)}")
```

### Delete Index (if needed)
```python
from pinecone import Pinecone
from config.settings import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
pc.delete_index(settings.PINECONE_INDEX_NAME)
```

### List All Indexes
```python
from pinecone import Pinecone
from config.settings import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
print("Available indexes:", pc.list_indexes().names())
```

## 💡 Best Practices

1. **Environment Selection**: Choose the Pinecone environment closest to your application
2. **Index Naming**: Use descriptive names for your indexes
3. **API Key Security**: Never commit API keys to version control
4. **Monitoring**: Monitor your Pinecone usage and costs
5. **Backup**: Consider backing up important vector data
6. **Serverless vs Standard**: Serverless indexes are easier to manage but may have higher costs

## 🔗 Useful Links

- [Pinecone Documentation](https://docs.pinecone.io/)
- [Pinecone Console](https://app.pinecone.io/)
- [Pinecone Python Client](https://github.com/pinecone-io/pinecone-python)
- [Voyage AI Embeddings](https://platform.voyageai.com/docs/embeddings)

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Pinecone documentation
3. Check the application logs in `legal_rag.log`
4. Run the test script: `python test_system.py`
5. Check your Pinecone console for account status and credits 