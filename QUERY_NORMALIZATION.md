# Query Normalization Feature

## Overview

The Legal RAG System now includes an intelligent query normalization feature that standardizes user queries by applying synonym replacements and text standardization. This improves search accuracy by ensuring that different ways of expressing the same concept are treated consistently.

## How It Works

The `normalize_query` function is integrated into the `ValidationUtils` class and automatically processes all queries through the API endpoints. It performs the following operations:

1. **Text Standardization**: Converts text to lowercase and removes extra whitespace
2. **Synonym Replacement**: Replaces common synonyms with standardized terms
3. **Legal Term Normalization**: Standardizes legal and insurance terminology

## Integrated Synonyms

The system includes comprehensive synonym mappings for legal and insurance terms:

### Medical/Insurance Terms
- **preexisting diseases**: `pre-existing disease`, `PED`, `existing illness`, `pre-existing condition`
- **expenses**: `coverage`, `limit`, `exclusion`, `claim amount`, `costs`, `medical expenses`
- **coverage**: `insurance coverage`, `policy coverage`, `benefits`, `protection`
- **deductible**: `deductible amount`, `deductible limit`, `out-of-pocket`
- **premium**: `insurance premium`, `monthly premium`, `annual premium`, `payment`
- **claim**: `insurance claim`, `claim filing`, `claim process`, `claim submission`
- **exclusion**: `excluded conditions`, `not covered`, `excluded items`, `limitations`
- **waiting period**: `waiting time`, `wait period`, `exclusion period`, `initial period`
- **renewal**: `policy renewal`, `renewal process`, `renewal terms`, `extension`
- **termination**: `policy termination`, `cancellation`, `end of coverage`, `discontinuation`

## Usage

### Automatic Usage
The normalization is automatically applied to all queries processed through the API endpoints:
- `/query/ask` - For asking legal questions
- `/query/search` - For searching documents

### Manual Usage
You can also use the function directly:

```python
from utils.validation import ValidationUtils

validation_utils = ValidationUtils()

# Normalize a query
normalized_query = validation_utils.normalize_query("What are the PED exclusions?")
# Result: "what are the preexisting diseases exclusions?"
```

### Through Validation
The normalization is also integrated into the query validation process:

```python
validation_result = validation_utils.validate_query("Tell me about claim amount limits")
normalized_query = validation_result["cleaned_query"]
# Result: "tell me about expenses limits"
```

## Example Transformations

| Original Query | Normalized Query |
|----------------|------------------|
| "What are the pre-existing disease exclusions?" | "what are the preexisting diseases exclusions?" |
| "How much is the PED coverage?" | "how much is the preexisting diseases coverage?" |
| "What are the claim amount limits?" | "what are the expenses limits?" |
| "Tell me about the insurance premium payment" | "tell me about the premium payment" |
| "What is the deductible amount?" | "what is the deductible?" |

## Benefits

1. **Improved Search Accuracy**: Different phrasings of the same concept return consistent results
2. **Better User Experience**: Users can use natural language without worrying about exact terminology
3. **Legal Domain Expertise**: Built-in understanding of legal and insurance terminology
4. **Consistent Results**: Standardized queries lead to more predictable search outcomes

## Configuration

The synonym mappings are defined in the `normalize_query` method within `utils/validation.py`. You can easily extend or modify the synonyms by editing this method:

```python
def normalize_query(self, query: str) -> str:
    # ... existing code ...
    
    synonyms = {
        "your_standard_term": ["synonym1", "synonym2", "synonym3"],
        # Add more mappings here
    }
    
    # ... rest of the method
```

## Testing

Run the test script to verify the normalization functionality:

```bash
python test_query_normalization.py
```

This will test various query transformations and edge cases to ensure the function works correctly.

## Integration Points

The query normalization is integrated at the following points in the system:

1. **API Routes** (`api/routes/query.py`): All query endpoints use the validation utility
2. **Validation Layer** (`utils/validation.py`): The `validate_query` method now includes normalization
3. **Search Processing**: Normalized queries are used for embedding generation and vector search

## Future Enhancements

Potential improvements to consider:

1. **Dynamic Synonym Loading**: Load synonyms from configuration files
2. **Context-Aware Normalization**: Different normalization rules for different document types
3. **Machine Learning**: Learn new synonyms from user interactions
4. **Multi-language Support**: Support for synonyms in different languages
5. **Domain-Specific Rules**: Specialized normalization for different legal domains

## Troubleshooting

### Query Not Being Normalized
- Check that you're using the API endpoints (`/query/ask` or `/query/search`)
- Verify that the validation utility is being imported correctly
- Check the logs for any error messages

### Unexpected Normalization
- Review the synonym mappings in the `normalize_query` method
- Test with the provided test script to understand the transformations
- Consider adding more specific synonyms if needed

### Performance Issues
- The normalization is lightweight and shouldn't impact performance
- If issues occur, check for very long queries or excessive synonym mappings 