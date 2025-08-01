# Keyword Anchoring Backup Feature

## Overview

The Legal RAG System now includes intelligent keyword anchoring backup that provides a fallback mechanism when semantic similarity search fails to return relevant results. This feature ensures that users always receive meaningful responses by directly searching for specific legal keywords in document chunks.

## Key Features

### 1. **Automatic Fallback Activation**
- **Smart Detection**: Automatically activates when semantic search returns no results
- **Threshold-Based**: Triggers when all similarity scores are below configured thresholds
- **Seamless Integration**: Works transparently with existing semantic search

### 2. **Intelligent Keyword Extraction**
- **Legal Term Recognition**: Extracts domain-specific legal keywords from queries
- **Category-Based**: Uses predefined legal keyword categories for comprehensive coverage
- **Context-Aware**: Considers query context and word relationships

### 3. **Advanced Relevance Scoring**
- **Keyword Density**: Calculates relevance based on keyword frequency in text
- **Position Weighting**: Gives higher scores to keywords appearing early in documents
- **Coverage Analysis**: Considers the percentage of query keywords found

### 4. **Enhanced Result Transparency**
- **Retrieval Method**: Clearly indicates whether results came from semantic search or keyword anchoring
- **Keyword Matches**: Shows which specific keywords were found in each result
- **Confidence Scoring**: Provides relevance scores for keyword-based results

## How It Works

### Keyword Anchoring Process

1. **Semantic Search Failure Detection**: Monitors semantic search results
2. **Keyword Extraction**: Extracts relevant legal keywords from the query
3. **Document Scanning**: Searches through available documents for keyword matches
4. **Relevance Scoring**: Calculates relevance scores for keyword matches
5. **Result Ranking**: Ranks results by keyword relevance and returns top matches

### Keyword Extraction Logic

```python
def _extract_keywords_from_query(self, query: str) -> List[str]:
    # Extract from legal categories
    for category, keywords in self.legal_keywords.items():
        for keyword in keywords:
            if keyword.lower() in query_lower:
                extracted_keywords.append(keyword)
    
    # Extract common legal terms
    legal_terms = [
        "pre-existing disease", "exclusion", "coverage", "claim", "deductible",
        "premium", "waiting period", "renewal", "termination", "policy"
    ]
    
    # Extract individual relevant words
    relevant_words = ["disease", "exclusion", "coverage", "claim", "deductible"]
```

### Relevance Scoring Algorithm

```python
def _calculate_keyword_relevance_score(self, text, matched_keywords, query_keywords):
    # Keyword density (40% weight)
    keyword_density = keyword_count / total_words
    
    # Keyword coverage (40% weight)
    keyword_coverage = matched_keywords / total_query_keywords
    
    # Position bonus (20% weight)
    position_bonus = sum((1 - normalized_position) * 0.2 for keyword in matched_keywords)
    
    # Combined score
    relevance_score = (keyword_density * 0.4 + 
                      keyword_coverage * 0.4 + 
                      position_bonus * 0.2)
```

## Configuration

### Environment Variables

```bash
# Keyword Anchoring Configuration
ENABLE_KEYWORD_ANCHORING=true          # Enable/disable keyword anchoring
KEYWORD_ANCHORING_PRIORITY=high        # Priority level (high/medium/low)
MAX_KEYWORD_RESULTS=3                  # Maximum keyword results to return
```

### Settings Class

```python
class Settings:
    # Keyword anchoring backup
    ENABLE_KEYWORD_ANCHORING = os.getenv("ENABLE_KEYWORD_ANCHORING", "true").lower() == "true"
    KEYWORD_ANCHORING_PRIORITY = os.getenv("KEYWORD_ANCHORING_PRIORITY", "high").lower()
    MAX_KEYWORD_RESULTS = int(os.getenv("MAX_KEYWORD_RESULTS", 3))
```

## Integration Points

### 1. **Enhanced Retrieval Engine**

The `AdvancedRetrievalEngine` class includes:

```python
def _apply_keyword_anchoring_backup(
    self,
    query: str,
    search_results: Dict[str, Any],
    return_count: int,
    filter_dict: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Apply keyword anchoring backup when semantic search fails"""
```

### 2. **Automatic Activation**

Keyword anchoring automatically activates in the main retrieval process:

```python
# Step 7: Apply keyword anchoring backup if no results
if not results and settings.ENABLE_KEYWORD_ANCHORING:
    logger.info("No semantic results found, applying keyword anchoring backup")
    keyword_results = self._apply_keyword_anchoring_backup(
        query=query,
        search_results=search_results,
        return_count=return_count,
        filter_dict=filter_dict
    )
    if keyword_results:
        return keyword_results
```

### 3. **Enhanced API Responses**

API responses now include keyword anchoring information:

```json
{
  "answer": "Generated answer...",
  "sources": [
    {
      "doc_id": "doc_123",
      "similarity_score": 0.85,
      "retrieval_method": "keyword_anchoring",
      "keyword_matches": ["pre-existing disease", "exclusion"],
      "section_title": "1.1 COVERAGE"
    }
  ],
  "confidence": 0.82
}
```

## Usage Examples

### Basic Usage

Keyword anchoring works automatically when semantic search fails:

```python
from vectordb.advanced_retrieval import retrieve_documents_advanced

# This will automatically use keyword anchoring if semantic search fails
results = retrieve_documents_advanced(
    query="What are the pre-existing disease exclusions?",
    threshold=0.8  # High threshold that might cause semantic search to fail
)
```

### API Usage

```bash
# Query that might trigger keyword anchoring
curl -X POST "http://localhost:8000/query/ask" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=What are the pre-existing disease exclusions?" \
  -d "similarity_threshold=0.9"
```

### Response Analysis

```python
# Check if results came from keyword anchoring
for result in results:
    if result.get('retrieval_method') == 'keyword_anchoring':
        print(f"Keyword matches: {result.get('keyword_matches', [])}")
        print(f"Relevance score: {result.get('similarity_score', 0):.3f}")
```

## Keyword Categories

### Legal Document Keywords

The system recognizes keywords from these categories:

1. **Pre-existing Diseases**
   - "pre-existing disease", "ped", "excl 01", "preexisting condition"

2. **Exclusions**
   - "exclusion", "excluded", "not covered", "limitations"

3. **Coverage**
   - "coverage", "covered", "benefits", "insurance coverage"

4. **Claims**
   - "claim", "claim filing", "claim process", "claim submission"

5. **Deductibles**
   - "deductible", "deductible amount", "out-of-pocket"

6. **Premiums**
   - "premium", "insurance premium", "monthly premium"

7. **Waiting Periods**
   - "waiting period", "waiting time", "wait period"

8. **Renewals**
   - "renewal", "policy renewal", "renewal process"

9. **Terminations**
   - "termination", "policy termination", "cancellation"

## Scenarios and Use Cases

### 1. **Semantic Search Failure**
- **Scenario**: Semantic search returns no results due to high threshold
- **Behavior**: Keyword anchoring automatically activates
- **Result**: Relevant documents found based on keyword matches

### 2. **Low Similarity Scores**
- **Scenario**: All semantic results have very low similarity scores
- **Behavior**: Keyword anchoring provides alternative results
- **Result**: Documents with keyword matches are returned

### 3. **Specific Legal Terms**
- **Scenario**: Query contains specific legal terminology
- **Behavior**: Keyword anchoring finds exact term matches
- **Result**: Highly relevant documents with legal term occurrences

### 4. **Fallback Reliability**
- **Scenario**: System needs to ensure result availability
- **Behavior**: Keyword anchoring guarantees minimum results
- **Result**: Users always receive some relevant information

## Benefits

### 1. **Improved Reliability**
- **Guaranteed Results**: Always provides some relevant results
- **Fallback Mechanism**: Handles semantic search failures gracefully
- **System Resilience**: Maintains functionality even with poor embeddings

### 2. **Enhanced User Experience**
- **Consistent Responses**: Users always get meaningful answers
- **Transparent Process**: Clear indication of retrieval method used
- **Relevant Results**: Focuses on legal domain-specific content

### 3. **Better Coverage**
- **Domain Expertise**: Leverages legal keyword knowledge
- **Comprehensive Search**: Covers both semantic and keyword-based retrieval
- **Flexible Matching**: Handles various query formulations

### 4. **System Transparency**
- **Method Indication**: Shows whether semantic or keyword search was used
- **Keyword Visibility**: Displays which keywords were matched
- **Confidence Scoring**: Provides relevance scores for all results

## Performance Considerations

### 1. **Processing Overhead**
- **Minimal Impact**: Only activates when semantic search fails
- **Efficient Scanning**: Uses optimized keyword matching algorithms
- **Limited Scope**: Only processes when necessary

### 2. **Memory Usage**
- **Keyword Storage**: Pre-defined keywords stored in memory
- **Document Access**: Efficient document retrieval for keyword search
- **Result Caching**: Can cache keyword search results

### 3. **Scalability**
- **Parallel Processing**: Keyword search can be parallelized
- **Indexed Keywords**: Can use keyword indexes for faster search
- **Configurable Limits**: Adjustable result limits

## Testing

### Run the Test Suite

```bash
python test_keyword_anchoring.py
```

### Test Coverage

The test suite covers:

1. **Keyword Extraction**: Various query patterns and legal terms
2. **Relevance Scoring**: Different keyword match scenarios
3. **Backup Activation**: Semantic search failure scenarios
4. **Settings Configuration**: Parameter validation
5. **Integration Scenarios**: End-to-end functionality
6. **Edge Cases**: Boundary conditions and error handling

### Example Test Output

```
🧪 Testing Keyword Extraction
📝 Query: 'What are the pre-existing disease exclusions?'
Extracted Keywords: ['pre-existing disease', 'exclusion']
Keyword Count: 2

📊 Testing Keyword Relevance Scoring
📋 High Relevance - Multiple Keywords:
Relevance Score: 0.850
✅ High relevance
```

## Troubleshooting

### Common Issues

1. **Keyword Anchoring Not Activating**
   - Check `ENABLE_KEYWORD_ANCHORING` setting
   - Verify semantic search is actually failing
   - Review keyword extraction logic

2. **Poor Keyword Matches**
   - Review keyword categories and terms
   - Check query preprocessing
   - Verify document content quality

3. **Performance Issues**
   - Monitor keyword search performance
   - Check document retrieval efficiency
   - Review result limits

### Debug Mode

Enable debug logging to see keyword anchoring details:

```python
import logging
logging.getLogger('vectordb.advanced_retrieval').setLevel(logging.DEBUG)
```

### Configuration Validation

```python
from config.settings import settings

# Validate keyword anchoring settings
assert settings.ENABLE_KEYWORD_ANCHORING in [True, False]
assert settings.MAX_KEYWORD_RESULTS > 0
assert settings.KEYWORD_ANCHORING_PRIORITY in ['high', 'medium', 'low']
```

## Future Enhancements

### 1. **Advanced Keyword Processing**
- **Machine Learning**: ML-based keyword extraction
- **Context Awareness**: Better understanding of keyword context
- **Dynamic Keywords**: Learn new keywords from user interactions

### 2. **Enhanced Scoring**
- **Semantic Keywords**: Consider semantic relationships between keywords
- **Document Structure**: Weight keywords based on document structure
- **User Feedback**: Incorporate user feedback into scoring

### 3. **Performance Optimization**
- **Keyword Indexing**: Create efficient keyword indexes
- **Caching**: Cache keyword search results
- **Parallel Processing**: Optimize for concurrent requests

### 4. **Advanced Features**
- **Hybrid Search**: Combine semantic and keyword search intelligently
- **Query Expansion**: Expand queries with related keywords
- **Personalization**: Adapt keyword preferences based on user behavior

## Summary

The Keyword Anchoring Backup feature significantly enhances the Legal RAG System by:

1. **Providing reliable fallback** when semantic search fails
2. **Ensuring consistent results** through intelligent keyword matching
3. **Maintaining transparency** with clear retrieval method indication
4. **Improving user experience** with guaranteed relevant responses
5. **Enhancing system resilience** with robust error handling

This integration transforms the system's reliability and ensures users always receive meaningful, relevant responses to their legal document queries. 