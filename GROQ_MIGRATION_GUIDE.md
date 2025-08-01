# Groq Migration Guide

## Overview

This guide explains the migration from Voyage AI to Groq for chat completions in the Legal RAG System. Voyage AI is still used for embeddings, but Groq is now used for generating responses.

## Changes Made

### 1. Configuration Updates

**New Environment Variables:**
- `GROQ_API_KEY`: Your Groq API key
- `GROQ_CHAT_MODEL`: Groq model to use (default: `llama3-8b-8192`)
- `GROQ_MAX_TOKENS`: Maximum tokens for responses (default: 1000)
- `GROQ_TEMPERATURE`: Temperature for response generation (default: 0.1)

**Removed Environment Variables:**
- `VOYAGE_CHAT_MODEL` (no longer needed)
- `VOYAGE_MAX_TOKENS` (replaced with Groq equivalents)
- `VOYAGE_TEMPERATURE` (replaced with Groq equivalents)

### 2. Dependencies

**Added:**
- `groq>=0.4.2`: Groq Python client

**Kept:**
- `voyageai>=0.3.4`: Still used for embeddings

### 3. Code Changes

- **LLM Client**: Updated to use Groq for chat completions
- **Settings**: Added Groq configuration, kept Voyage AI for embeddings
- **API Validation**: Now requires both Voyage AI and Groq API keys

## Setup Instructions

### 1. Get Groq API Key

1. Sign up at [Groq Console](https://console.groq.com/)
2. Create an API key
3. Copy the API key

### 2. Update Environment Variables

Add to your `.env` file:

```bash
# Groq Configuration (for chat completions)
GROQ_API_KEY=your_groq_api_key_here
GROQ_CHAT_MODEL=llama3-8b-8192
GROQ_MAX_TOKENS=1000
GROQ_TEMPERATURE=0.1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test the Integration

```bash
python test_groq_integration.py
```

## Available Groq Models

The system is configured to use `llama3-8b-8192` by default, but you can change it to any of these models:

- `llama3-8b-8192` (default, fast and efficient)
- `llama3-70b-8192` (larger, more capable)
- `mixtral-8x7b-32768` (good balance)
- `gemma2-9b-it` (Google's Gemma model)

## What's Unchanged

- **Embeddings**: Still use Voyage AI (`voyage-large-2`)
- **Vector Database**: Still use Pinecone
- **Document Processing**: All existing functionality remains the same
- **API Endpoints**: No changes to existing endpoints
- **Response Formatting**: Same output format

## Troubleshooting

### Common Issues

1. **"GROQ_API_KEY not found"**
   - Make sure you've added the Groq API key to your `.env` file
   - Restart your application after adding the key

2. **"Failed to generate response"**
   - Check your Groq API key is valid
   - Verify you have sufficient credits in your Groq account
   - Check the model name is correct

3. **Import errors**
   - Run `pip install groq>=0.4.2`
   - Make sure you're using the updated requirements.txt

### Testing

Use the provided test script to verify everything works:

```bash
python test_groq_integration.py
```

## Benefits of Groq

- **Speed**: Groq is known for very fast inference
- **Cost**: Generally more cost-effective than many alternatives
- **Reliability**: Stable API with good uptime
- **Models**: Access to high-quality open-source models

## Rollback Plan

If you need to rollback to the previous implementation:

1. Revert the changes in `llm_service/llm_client.py`
2. Remove Groq configuration from `config/settings.py`
3. Remove `groq` from `requirements.txt`
4. Update environment variables to use Voyage AI for chat (if HTTP API becomes available)

## Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify your API keys are correct
3. Test with the provided test script
4. Check Groq's status page for any service issues 