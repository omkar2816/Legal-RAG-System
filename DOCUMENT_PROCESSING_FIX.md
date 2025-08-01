# DOCUMENT PROCESSING FIXES

1. **Embedding API Quota Exceeded**: 429 errors preventing embedding generation
2. **Fallback**: Falls back when embedding API fails

### **Option 1: Use Voyage AI API (Recommended)**
1. **Add Credits to Voyage AI Account**:
- Go to https://platform.voyageai.com/account/billing
2. **Set VOYAGE_API_KEY in .env**

The system now automatically falls back to mock embeddings when the embedding API fails. This allows you to:
- Continue testing and development
- Avoid downtime due to quota issues

- Embedding generation (quota exceeded)

1. **Add Voyage AI API Credits**:
- Go to https://platform.voyageai.com/account/billing 