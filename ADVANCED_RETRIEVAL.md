# Advanced Retrieval System

## Overview

The Legal RAG System now includes an advanced retrieval engine that combines semantic similarity with structural ranking for significantly improved document retrieval accuracy. This system goes beyond simple vector similarity to understand legal document structure and content relevance.

## Key Features

### 1. **Semantic + Structural Ranking**
- **Semantic Similarity**: Uses vector embeddings for initial retrieval
- **Structural Ranking**: Applies legal domain knowledge for re-ranking
- **Hybrid Approach**: Combines both methods for optimal results

### 2. **Legal Domain Intelligence**
- **Keyword Categories**: Pre-configured legal and insurance terminology
- **Content Relevance**: Understands document sections and legal structure
- **Intent Recognition**: Analyzes query intent and legal categories

### 3. **Enhanced Query Processing**
- **Query Normalization**: Standardizes queries using synonym replacement
- **Intent Analysis**: Identifies primary and secondary legal categories
- **Confidence Scoring**: Provides confidence levels for query understanding

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│   Query         │───▶│   Semantic      │
│                 │    │   Normalization │    │   Retrieval     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Intent        │    │   Structural    │    │   Final         │
│   Analysis      │◀───│   Ranking       │◀───│   Ranking       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Legal Keyword Categories

The system includes comprehensive keyword mappings for legal and insurance domains:

### Medical/Insurance Terms
- **preexisting_diseases**: `pre-existing disease`, `PED`, `excl 01`, `preexisting condition`
- **exclusions**: `exclusion`, `excluded`, `not covered`, `limitations`
- **coverage**: `coverage`, `covered`, `benefits`, `insurance coverage`
- **claims**: `claim`, `claim filing`, `claim process`, `claim submission`
- **deductibles**: `deductible`, `deductible amount`, `out-of-pocket`
- **premiums**: `premium`, `insurance premium`, `monthly premium`
- **waiting_periods**: `waiting period`, `waiting time`, `wait period`
- **renewals**: `renewal`, `policy renewal`, `renewal process`
- **terminations**: `termination`, `policy termination`, `cancellation`

## Ranking System

### Structural Rank Levels

1. **Rank 1 (Highest Priority)**: Exact category matches
   - Query and document both contain related legal keywords
   - Example: Query about "PED exclusions" matches document with "pre-existing disease"

2. **Rank 2 (Medium Priority)**: General legal term matches
   - Document contains general legal terms related to query
   - Example: Query about "exclusions" matches document with "limitations"

3. **Rank 3 (Lowest Priority)**: Semantic similarity only
   - No specific legal keyword matches
   - Relies purely on vector similarity

### Ranking Algorithm

```python
def calculate_structural_rank(text, query):
    # Check for exact keyword category matches
    for category, keywords in legal_keywords.items():
        if any(keyword in text.lower() for keyword in keywords):
            if any(keyword in query.lower() for keyword in keywords):
                return 1  # Highest priority
    
    # Check for general legal terms
    if any(term in text.lower() for term in ['exclusion', 'limitation']):
        if any(term in query.lower() for term in ['exclusion', 'limit']):
            return 2  # Medium priority
    
    return 3  # Lowest priority
```

## API Endpoints

### 1. Enhanced `/query/ask` Endpoint

**POST** `/query/ask`

Now includes advanced retrieval with structural ranking:

```json
{
  "question": "What are the pre-existing disease exclusions?",
  "top_k": 5,
  "similarity_threshold": 0.7
}
```

**Response includes structural ranking:**
```json
{
  "answer": "Based on the policy documents...",
  "sources": [
    {
      "doc_id": "policy_001",
      "doc_title": "Health Insurance Policy",
      "section_title": "Exclusions",
      "similarity_score": 0.85,
      "structural_rank": 1,
      "page_number": 15,
      "chunk_text": "Pre-existing diseases are excluded..."
    }
  ],
  "confidence": 0.82,
  "total_sources": 3
}
```

### 2. Enhanced `/query/search` Endpoint

**GET** `/query/search`

Returns documents with structural ranking information:

```json
{
  "query": "what are the preexisting diseases exclusions?",
  "results": [
    {
      "doc_id": "policy_001",
      "doc_title": "Health Insurance Policy",
      "section_title": "Exclusions",
      "similarity_score": 0.85,
      "structural_rank": 1,
      "text": "Pre-existing diseases are excluded...",
      "word_count": 150,
      "legal_density": 0.8,
      "page_number": 15,
      "chunk_id": "chunk_001"
    }
  ],
  "total_results": 5
}
```

### 3. New `/query/analyze` Endpoint

**GET** `/query/analyze`

Analyzes query intent and legal categories:

```json
{
  "query": "What are the PED exclusions?",
  "normalized_query": "what are the preexisting diseases exclusions?",
  "intent_analysis": {
    "primary_category": "preexisting_diseases",
    "secondary_categories": ["exclusions"],
    "confidence": 0.67,
    "keywords_found": ["ped", "exclusions"]
  },
  "warnings": ["Query was normalized for better search results"]
}
```

## Usage Examples

### Basic Usage

```python
from vectordb.advanced_retrieval import retrieve_documents_advanced

# Simple retrieval
results = retrieve_documents_advanced(
    query="What are the pre-existing disease exclusions?",
    top_k=10,
    threshold=0.25,
    return_count=3
)

for result in results:
    print(f"Rank: {result['structural_rank']}, Score: {result['similarity_score']:.3f}")
    print(f"Text: {result['text'][:100]}...")
```

### Query Intent Analysis

```python
from vectordb.advanced_retrieval import analyze_query_intent

# Analyze query intent
intent = analyze_query_intent("How do I file a claim?")
print(f"Primary Category: {intent['primary_category']}")
print(f"Confidence: {intent['confidence']:.2f}")
```

### Custom Keyword Addition

```python
from vectordb.advanced_retrieval import advanced_retrieval_engine

# Add custom legal keywords
engine = advanced_retrieval_engine
engine.add_legal_keywords(
    "custom_category", 
    ["custom_term1", "custom_term2", "custom_term3"]
)
```

## Configuration

### Legal Keywords

You can customize the legal keywords by modifying the `AdvancedRetrievalEngine` class:

```python
class AdvancedRetrievalEngine:
    def __init__(self):
        self.legal_keywords = {
            "your_category": ["keyword1", "keyword2", "keyword3"],
            # Add more categories as needed
        }
```

### Ranking Parameters

Adjust ranking behavior by modifying the `calculate_structural_rank` method:

```python
def calculate_structural_rank(self, text: str, query: str) -> int:
    # Customize ranking logic here
    # Return 1, 2, or 3 based on your criteria
    pass
```

## Performance Benefits

### 1. **Improved Relevance**
- Structural ranking prioritizes legally relevant content
- Reduces false positives from semantic-only search
- Better handling of legal terminology variations

### 2. **Enhanced User Experience**
- More accurate answers to legal questions
- Better source selection for LLM context
- Consistent results across similar queries

### 3. **Domain Expertise**
- Built-in understanding of legal document structure
- Automatic recognition of important legal sections
- Context-aware ranking based on query intent

## Testing

Run the test script to verify functionality:

```bash
python test_advanced_retrieval.py
```

This will test:
- Query normalization
- Structural ranking
- Query intent analysis
- Legal keyword management
- Edge cases and error handling

## Integration Points

### 1. **API Layer**
- All query endpoints now use advanced retrieval
- Enhanced response format includes ranking information
- New analysis endpoint for query understanding

### 2. **Validation Layer**
- Query normalization integrated with existing validation
- Consistent processing across all endpoints
- Warning system for query modifications

### 3. **Vector Database**
- Leverages existing Pinecone integration
- Maintains compatibility with current embeddings
- Enhanced filtering and ranking capabilities

## Future Enhancements

### 1. **Dynamic Learning**
- Learn new keywords from user interactions
- Adapt ranking based on query patterns
- Personalized relevance scoring

### 2. **Multi-Domain Support**
- Extend to other legal domains (contracts, regulations, etc.)
- Domain-specific keyword categories
- Specialized ranking rules per domain

### 3. **Advanced Analytics**
- Query pattern analysis
- Performance metrics and optimization
- A/B testing for ranking algorithms

### 4. **Machine Learning Integration**
- Train ranking models on user feedback
- Automatic keyword discovery
- Semantic similarity improvements

## Troubleshooting

### Common Issues

1. **No Results Returned**
   - Check similarity threshold (try lowering it)
   - Verify documents are properly indexed
   - Ensure query normalization is working

2. **Poor Ranking Results**
   - Review legal keyword categories
   - Check document structure and metadata
   - Verify query intent analysis

3. **Performance Issues**
   - Monitor query processing time
   - Check embedding generation speed
   - Optimize keyword matching algorithms

### Debug Mode

Enable debug logging to see detailed ranking information:

```python
import logging
logging.getLogger('vectordb.advanced_retrieval').setLevel(logging.DEBUG)
```

## Summary

The Advanced Retrieval System significantly enhances the Legal RAG System by:

1. **Combining semantic and structural ranking** for better relevance
2. **Understanding legal domain terminology** and document structure
3. **Providing query intent analysis** for better user understanding
4. **Maintaining backward compatibility** with existing API endpoints
5. **Offering extensible architecture** for future enhancements

This integration transforms the system from a basic vector search to an intelligent legal document retrieval engine that understands both the meaning and structure of legal content. 