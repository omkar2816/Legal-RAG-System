# Enhanced Similarity Threshold Handling

## Overview

The Legal RAG System now includes sophisticated similarity threshold handling that intelligently filters search results based on relevance scores. This feature ensures that only highly relevant content is returned while maintaining flexibility to guarantee minimum result requirements.

## Key Features

### 1. **Adaptive Threshold Calculation**
- **Dynamic Adjustment**: Thresholds adjust based on score distribution
- **Context-Aware**: Considers the range and distribution of all scores
- **Configurable Bounds**: Respects minimum and maximum threshold limits

### 2. **Intelligent Filtering**
- **Score-Based Filtering**: Filters out results below the effective threshold
- **Minimum Results Guarantee**: Ensures a minimum number of results are returned
- **Threshold Relaxation**: Automatically lowers threshold if insufficient results

### 3. **Enhanced Configuration**
- **Multiple Threshold Levels**: Minimum, medium, and high similarity thresholds
- **Adaptive Behavior**: Enable/disable adaptive threshold adjustment
- **Minimum Results**: Configurable minimum results requirement

## How It Works

### Threshold Calculation Process

1. **Base Threshold**: Start with the user-specified threshold
2. **Score Analysis**: Analyze the distribution of all similarity scores
3. **Adaptive Adjustment**: Adjust threshold based on score characteristics
4. **Bounds Enforcement**: Ensure threshold stays within configured limits
5. **Result Filtering**: Apply effective threshold to filter results

### Adaptive Threshold Logic

```python
def _calculate_effective_threshold(self, score, base_threshold, adaptive, all_scores):
    if not adaptive:
        return base_threshold
    
    effective_threshold = base_threshold
    
    # Adjust based on score distribution
    if all_scores:
        max_score = max(all_scores)
        min_score = min(all_scores)
        score_range = max_score - min_score
        
        # Wide range: be more selective
        if score_range > 0.5:
            effective_threshold = max(effective_threshold, min_score + score_range * 0.3)
        
        # High score: be more selective
        if score > HIGH_SIMILARITY_THRESHOLD:
            effective_threshold = max(effective_threshold, MEDIUM_SIMILARITY_THRESHOLD)
        
        # Low score: be more lenient
        elif score < MIN_SIMILARITY_THRESHOLD:
            effective_threshold = min(effective_threshold, MIN_SIMILARITY_THRESHOLD)
    
    # Ensure within bounds
    return max(MIN_SIMILARITY_THRESHOLD, min(effective_threshold, HIGH_SIMILARITY_THRESHOLD))
```

### Minimum Results Guarantee

If the number of results after filtering is below the minimum requirement:

1. **Threshold Relaxation**: Lower the threshold to include more results
2. **Re-processing**: Re-process all candidates with the adjusted threshold
3. **Result Return**: Return the minimum required number of results

## Configuration

### Environment Variables

```bash
# Threshold Configuration
MIN_SIMILARITY_THRESHOLD=0.2          # Minimum acceptable similarity score
MEDIUM_SIMILARITY_THRESHOLD=0.5       # Medium similarity threshold
HIGH_SIMILARITY_THRESHOLD=0.8         # High similarity threshold

# Behavior Configuration
ENABLE_THRESHOLD_FILTERING=true       # Enable/disable threshold filtering
ADAPTIVE_THRESHOLD=true               # Enable/disable adaptive threshold
MIN_RESULTS_REQUIRED=1                # Minimum results to return
```

### Settings Class

```python
class Settings:
    # Advanced Retrieval Thresholds
    MIN_SIMILARITY_THRESHOLD = float(os.getenv("MIN_SIMILARITY_THRESHOLD", 0.2))
    HIGH_SIMILARITY_THRESHOLD = float(os.getenv("HIGH_SIMILARITY_THRESHOLD", 0.8))
    MEDIUM_SIMILARITY_THRESHOLD = float(os.getenv("MEDIUM_SIMILARITY_THRESHOLD", 0.5))
    
    # Threshold-based filtering
    ENABLE_THRESHOLD_FILTERING = os.getenv("ENABLE_THRESHOLD_FILTERING", "true").lower() == "true"
    ADAPTIVE_THRESHOLD = os.getenv("ADAPTIVE_THRESHOLD", "true").lower() == "true"
    MIN_RESULTS_REQUIRED = int(os.getenv("MIN_RESULTS_REQUIRED", 1))
```

## Integration Points

### 1. **Enhanced Retrieval Engine**

The `AdvancedRetrievalEngine` class includes:

```python
def retrieve_documents(
    self, 
    query: str, 
    top_k: int = 10, 
    threshold: float = 0.25,
    filter_dict: Optional[Dict[str, Any]] = None,
    return_count: int = 3,
    adaptive_threshold: bool = True
) -> List[Dict[str, Any]]:
    """Advanced document retrieval with enhanced threshold handling"""
```

### 2. **API Endpoints**

All query endpoints now use enhanced threshold handling:

```python
# In /query/ask endpoint
advanced_results = retrieve_documents_advanced(
    query=validation_result["cleaned_query"],
    top_k=top_k,
    threshold=similarity_threshold,
    filter_dict=filter_dict if filter_dict else None,
    return_count=top_k,
    adaptive_threshold=settings.ADAPTIVE_THRESHOLD
)
```

### 3. **Enhanced Response Format**

API responses now include threshold information:

```json
{
  "answer": "Generated answer...",
  "sources": [
    {
      "doc_id": "doc_123",
      "similarity_score": 0.85,
      "threshold_used": 0.75,
      "structural_rank": 1,
      "section_title": "1.1 COVERAGE"
    }
  ],
  "confidence": 0.82
}
```

## Usage Examples

### Basic Usage

```python
from vectordb.advanced_retrieval import retrieve_documents_advanced

# Basic retrieval with default threshold
results = retrieve_documents_advanced(
    query="What are the pre-existing disease exclusions?",
    threshold=0.3
)
```

### Advanced Usage

```python
# Custom threshold with adaptive behavior
results = retrieve_documents_advanced(
    query="How do I file a claim?",
    threshold=0.5,
    adaptive_threshold=True,
    return_count=5
)
```

### API Usage

```bash
# Query with custom threshold
curl -X POST "http://localhost:8000/query/ask" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=What are the coverage limits?" \
  -d "similarity_threshold=0.6" \
  -d "top_k=3"
```

## Threshold Scenarios

### 1. **High Quality Results**
- **Scenario**: Many high-scoring results available
- **Behavior**: Uses higher threshold for selectivity
- **Result**: Returns only the most relevant content

### 2. **Limited Results**
- **Scenario**: Few results meet the base threshold
- **Behavior**: Relaxes threshold to meet minimum requirement
- **Result**: Returns available results with lower confidence

### 3. **Mixed Quality**
- **Scenario**: Wide range of similarity scores
- **Behavior**: Adjusts threshold based on score distribution
- **Result**: Balances quality and quantity

### 4. **Poor Quality**
- **Scenario**: All results have low similarity scores
- **Behavior**: Uses minimum threshold to ensure results
- **Result**: Returns best available with appropriate warnings

## Benefits

### 1. **Improved Result Quality**
- **Relevance Filtering**: Only returns highly relevant content
- **Score-Based Selection**: Prioritizes results with higher similarity
- **Context Awareness**: Considers overall result distribution

### 2. **Flexible Behavior**
- **Adaptive Adjustment**: Automatically adjusts to result quality
- **Minimum Guarantee**: Ensures users always get some results
- **Configurable**: Easy to tune for different use cases

### 3. **Enhanced User Experience**
- **Consistent Results**: Predictable result quality
- **Transparent Thresholds**: Users can see what thresholds were used
- **Confidence Indication**: Clear indication of result relevance

### 4. **System Reliability**
- **Fallback Behavior**: Graceful handling of poor result sets
- **Performance Optimization**: Reduces processing of irrelevant content
- **Debugging Support**: Enhanced logging for troubleshooting

## Performance Considerations

### 1. **Processing Overhead**
- **Minimal Impact**: Threshold calculation is fast
- **Single Pass**: Processes scores in one iteration
- **Efficient Filtering**: Early termination for low-scoring results

### 2. **Memory Usage**
- **Score Collection**: Stores scores for distribution analysis
- **Result Filtering**: Filters in-place without additional storage
- **Optimized**: Minimal memory overhead

### 3. **Scalability**
- **Linear Complexity**: O(n) where n is number of results
- **Parallel Processing**: Compatible with concurrent requests
- **Caching Friendly**: Threshold calculations can be cached

## Testing

### Run the Test Suite

```bash
python test_threshold_handling.py
```

### Test Coverage

The test suite covers:

1. **Threshold Calculation**: Various score scenarios
2. **Filtering Logic**: Different threshold levels
3. **Minimum Results**: Guarantee behavior
4. **Settings Configuration**: Parameter validation
5. **Edge Cases**: Boundary conditions and errors

### Example Test Output

```
🧪 Testing Threshold Calculation
📊 High Score - Should be selective:
  Score: 0.900
  Base Threshold: 0.300
  Effective Threshold: 0.500
  ✅ Threshold within bounds

🔍 Testing Threshold Filtering
📋 High Threshold (0.8):
  Expected: 1 results
  Actual: 1 results
    - Doc A: Score=0.900, Threshold=0.800
```

## Troubleshooting

### Common Issues

1. **No Results Returned**
   - Check `MIN_RESULTS_REQUIRED` setting
   - Verify `MIN_SIMILARITY_THRESHOLD` is not too high
   - Review document quality and embeddings

2. **Too Many Low-Quality Results**
   - Increase `HIGH_SIMILARITY_THRESHOLD`
   - Enable `ADAPTIVE_THRESHOLD`
   - Adjust base threshold in API calls

3. **Inconsistent Threshold Behavior**
   - Check `ADAPTIVE_THRESHOLD` setting
   - Verify threshold bounds configuration
   - Review score distribution in logs

### Debug Mode

Enable debug logging to see threshold calculations:

```python
import logging
logging.getLogger('vectordb.advanced_retrieval').setLevel(logging.DEBUG)
```

### Configuration Validation

```python
from config.settings import settings

# Validate threshold hierarchy
assert settings.MIN_SIMILARITY_THRESHOLD < settings.MEDIUM_SIMILARITY_THRESHOLD
assert settings.MEDIUM_SIMILARITY_THRESHOLD < settings.HIGH_SIMILARITY_THRESHOLD
assert settings.MIN_RESULTS_REQUIRED > 0
```

## Future Enhancements

### 1. **Machine Learning Integration**
- **Learned Thresholds**: ML-based threshold optimization
- **Query-Specific Thresholds**: Different thresholds for different query types
- **User Feedback**: Threshold adjustment based on user interactions

### 2. **Advanced Filtering**
- **Multi-Criteria Filtering**: Combine similarity with other factors
- **Dynamic Weighting**: Adjust importance of different criteria
- **Contextual Filtering**: Consider query context and user history

### 3. **Performance Optimization**
- **Threshold Caching**: Cache threshold calculations
- **Batch Processing**: Optimize for bulk queries
- **Async Processing**: Non-blocking threshold calculations

### 4. **Enhanced Monitoring**
- **Threshold Analytics**: Track threshold effectiveness
- **Quality Metrics**: Monitor result quality over time
- **A/B Testing**: Compare different threshold strategies

## Summary

The Enhanced Similarity Threshold Handling feature significantly improves the Legal RAG System by:

1. **Providing intelligent result filtering** based on similarity scores
2. **Ensuring consistent result quality** through adaptive threshold adjustment
3. **Guaranteeing minimum result availability** with threshold relaxation
4. **Offering flexible configuration** for different use cases
5. **Maintaining system reliability** with robust fallback behavior

This integration transforms the system's ability to provide relevant, high-quality search results while maintaining flexibility and user experience. 