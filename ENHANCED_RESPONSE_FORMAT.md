# Enhanced Response Format and Structured Responses

## Overview

The Legal RAG System now provides enhanced, structured responses with comprehensive metadata, better categorization, and improved explainability. This enhancement significantly improves the quality and usefulness of responses for legal document queries.

## Key Features

### 1. Structured Response Format

All responses now follow a consistent, structured format with the following components:

```json
{
  "response_id": "resp_a1b2c3d4",
  "timestamp": "2024-01-01T12:00:00Z",
  "answer": "The policy covers hospitalization expenses up to ₹5,00,000 per year...",
  "response_type": "coverage",
  "category": "coverage",
  "query": {
    "original": "What is the coverage limit?",
    "processed": "What is the coverage limit?",
    "language": "en",
    "intent": {
      "primary_intent": "coverage",
      "all_intents": ["coverage", "information_seeking"],
      "complexity": "medium"
    }
  },
  "confidence": {
    "score": 0.85,
    "level": "high",
    "breakdown": {
      "overall": 0.85,
      "source_relevance": 0.88,
      "response_completeness": 0.9,
      "citation_quality": 0.8
    }
  },
  "sources": {
    "total_count": 2,
    "documents": [...],
    "coverage": {
      "documents": 1,
      "pages": 1,
      "sections": 1,
      "total_chunks": 2
    }
  },
  "search_parameters": {
    "threshold_used": 0.7,
    "adaptive_threshold": true,
    "retrieval_method": "semantic_search"
  },
  "quality_indicators": {
    "completeness": 0.9,
    "specificity": 0.85,
    "citation_count": 2
  },
  "warnings": [...],
  "recommendations": [...],
  "enhanced_metadata": {...},
  "explainability": {...}
}
```

### 2. Response Categorization

Responses are automatically categorized based on content and query intent:

- **direct_answer**: Direct factual responses
- **procedural**: Step-by-step instructions
- **exclusion**: Information about what's not covered
- **coverage**: Information about what's covered
- **claim**: Claim-related information
- **waiting_period**: Time-based restrictions
- **premium**: Payment and cost information
- **renewal**: Policy renewal information
- **termination**: Policy termination details
- **limitation**: Coverage limitations
- **general**: General information

### 3. Confidence Scoring

Enhanced confidence scoring with detailed breakdown:

- **Overall Score**: Combined confidence metric
- **Source Relevance**: How well sources match the query
- **Response Completeness**: How complete the answer is
- **Citation Quality**: Quality of policy citations

Confidence levels:
- **High**: 0.8-1.0
- **Medium**: 0.6-0.79
- **Low**: 0.4-0.59
- **Very Low**: 0.0-0.39

### 4. Source Analysis

Comprehensive source information including:

- Document coverage metrics
- Page and section analysis
- Retrieval method identification
- Citation detection
- Legal density scoring

### 5. Quality Indicators

Response quality metrics:

- **Completeness**: How complete the answer is
- **Specificity**: How specific and detailed the response is
- **Citation Count**: Number of policy citations

### 6. Enhanced Warnings and Recommendations

Structured warnings and recommendations with:

- **Type**: Warning/recommendation category
- **Severity**: Low/Medium/High/Critical
- **Message**: Clear description
- **Suggestion**: Actionable advice
- **Examples**: Specific examples when applicable

### 7. Query Intent Analysis

Automatic analysis of query intent:

- **Primary Intent**: Main query purpose
- **All Intents**: All detected intents
- **Complexity**: Query complexity level

Intent types:
- information_seeking
- procedural
- coverage
- exclusion
- financial
- temporal
- claim

### 8. Explainability Information

Comprehensive explainability data for audit trails:

- **Query Analysis**: Detailed query breakdown
- **Source Analysis**: Source quality and coverage
- **Response Quality**: Response quality metrics
- **Audit Trail**: Complete processing history

## API Endpoints

### 1. Enhanced Query Endpoint (`/query/ask`)

Returns structured responses with comprehensive metadata:

```python
POST /query/ask?question=What is the waiting period?&top_k=5&similarity_threshold=0.7
```

Response includes:
- Structured answer with citations
- Confidence scoring
- Source analysis
- Quality indicators
- Warnings and recommendations

### 2. Enhanced Search Endpoint (`/query/search`)

Returns enhanced search results:

```python
GET /query/search?query=waiting period&top_k=10
```

Features:
- Enhanced result metadata
- Coverage analysis
- Citation detection
- Quality scoring

### 3. Enhanced Analysis Endpoint (`/query/analyze`)

Provides detailed query analysis:

```python
GET /query/analyze?query=What is the coverage limit?
```

Includes:
- Intent analysis
- Complexity scoring
- Legal categorization
- Recommendations

### 4. Enhanced Suggestions Endpoint (`/query/suggest`)

Returns categorized suggestions:

```python
GET /query/suggest
```

Features:
- Categorized suggestions
- Complexity levels
- Expected response types
- Metadata

## Response Schema

### Core Response Structure

```python
@dataclass
class StructuredResponse:
    response_id: str
    timestamp: Optional[str]
    answer: str
    response_type: str
    category: str
    query: QueryInfo
    confidence: ConfidenceInfo
    sources: SourcesInfo
    search_parameters: SearchParameters
    quality_indicators: QualityIndicators
    warnings: List[Warning]
    recommendations: List[Recommendation]
    enhanced_metadata: Optional[EnhancedMetadata] = None
    explainability: Optional[ExplainabilityInfo] = None
```

### Validation

All responses are validated using `ResponseSchemaValidator`:

```python
validation_result = ResponseSchemaValidator.validate_response(response)
if validation_result["valid"]:
    print("Response is valid")
else:
    print(f"Validation errors: {validation_result['errors']}")
```

## Usage Examples

### 1. Basic Query

```python
import requests

response = requests.post("http://localhost:8000/query/ask", 
    params={"question": "What is the waiting period?"})

print(f"Answer: {response.json()['answer']}")
print(f"Confidence: {response.json()['confidence']['level']}")
print(f"Sources: {response.json()['sources']['total_count']}")
```

### 2. Search with Filters

```python
response = requests.get("http://localhost:8000/query/search",
    params={"query": "coverage limit", "top_k": 10})

for result in response.json()['results']:
    print(f"Document: {result['doc_title']}")
    print(f"Score: {result['similarity_score']}")
    print(f"Preview: {result['text_preview']}")
```

### 3. Query Analysis

```python
response = requests.get("http://localhost:8000/query/analyze",
    params={"query": "How do I file a claim?"})

analysis = response.json()
print(f"Intent: {analysis['analysis']['intent_analysis']['primary_intent']}")
print(f"Complexity: {analysis['analysis']['complexity_score']['complexity_level']}")
```

## Benefits

### 1. Improved User Experience

- **Structured Information**: Clear organization of response data
- **Confidence Indicators**: Users know how reliable the answer is
- **Actionable Recommendations**: Clear guidance for better results
- **Source Transparency**: Users can verify information sources

### 2. Better Debugging and Monitoring

- **Response IDs**: Unique identifiers for tracking
- **Detailed Metadata**: Comprehensive response information
- **Quality Metrics**: Objective quality indicators
- **Audit Trails**: Complete processing history

### 3. Enhanced Analytics

- **Query Patterns**: Understanding user needs
- **Response Quality**: Tracking system performance
- **Source Effectiveness**: Analyzing document coverage
- **User Behavior**: Understanding interaction patterns

### 4. Legal Compliance

- **Citation Tracking**: Proper attribution to policy sections
- **Source Verification**: Clear source identification
- **Audit Trails**: Complete processing records
- **Quality Assurance**: Structured quality metrics

## Testing

Run the test script to verify enhanced response functionality:

```bash
python test_enhanced_response_format.py
```

This will test:
- Enhanced response formatting
- Response schema validation
- Query analysis features
- Comprehensive response structure

## Migration Guide

### From Old Format

The enhanced format is backward compatible. Old responses are automatically converted:

```python
# Old format still works
old_response = {
    "answer": "The waiting period is 48 months.",
    "sources": [...],
    "confidence": 0.85
}

# Automatically enhanced
enhanced_response = response_formatter.format_response(
    answer=old_response["answer"],
    sources=old_response["sources"],
    confidence=old_response["confidence"],
    query="What is the waiting period?",
    threshold_used=0.7
)
```

### API Changes

- All existing endpoints continue to work
- New enhanced fields are optional
- Backward compatibility maintained
- Gradual migration supported

## Configuration

Enhanced response features can be configured:

```python
from llm_service.response_formatter import ResponseConfig

config = ResponseConfig(
    include_timestamps=True,
    include_response_id=True,
    include_metadata=True,
    include_explainability=True,
    format_type="enhanced_structured"
)

formatter = EnhancedLegalResponseFormatter(config)
```

## Future Enhancements

Planned improvements:

1. **Multi-language Support**: Enhanced internationalization
2. **Custom Response Types**: User-defined response categories
3. **Advanced Analytics**: Deeper response analysis
4. **Machine Learning**: Adaptive response optimization
5. **Real-time Feedback**: User feedback integration

## Conclusion

The enhanced response format provides a comprehensive, structured approach to legal document queries. It improves user experience, enables better monitoring, and ensures legal compliance while maintaining backward compatibility. 