# Policy Section Chunking Feature

## Overview

The Legal RAG System now includes intelligent policy section chunking that automatically detects and chunks policy documents by their numbered sections (e.g., 1.1, 2.3, 4.5). This provides more meaningful document segmentation for policy documents and improves retrieval accuracy.

## Key Features

### 1. **Automatic Section Detection**
- Detects numbered sections like "1.1 COVERAGE", "2.3 EXCLUSIONS"
- Handles various section numbering formats (1.1, 2.3, 10.5, etc.)
- Preserves section titles and content relationships

### 2. **Document Type-Aware Chunking**
- **Policy Documents**: Uses section-based chunking
- **Contract Documents**: Uses legal section chunking
- **Generic Documents**: Uses sliding window chunking

### 3. **Enhanced Metadata**
- Section anchors (e.g., "1.1", "2.3")
- Section types and chunking methods
- Word counts and content analysis

## How It Works

### Policy Section Detection

The system uses regex patterns to identify numbered sections:

```python
# Pattern: \d+(\.\d+)?\s+[A-Z][^\n]*
# Matches: "1.1 COVERAGE", "2.3 EXCLUSIONS", "10.5 CLAIMS"
```

### Chunking Process

1. **Text Cleaning**: Removes excessive whitespace and formatting
2. **Section Detection**: Identifies numbered sections using regex
3. **Content Extraction**: Separates section titles from content
4. **Metadata Generation**: Creates rich metadata for each chunk
5. **Chunk Creation**: Produces structured chunks with section information

## Integration Points

### 1. **Enhanced Chunker Class**

The `LegalDocumentChunker` class now includes:

```python
def chunk_policy_by_section(self, pdf_text: str) -> List[Dict[str, Any]]:
    """Chunk policy documents by numbered sections"""
    
def chunk_by_document_type(self, text: str, doc_type: str) -> List[Dict[str, Any]]:
    """Choose appropriate chunking method based on document type"""
```

### 2. **Updated Ingestion Process**

The document ingestion now automatically selects chunking method:

```python
# In api/routes/ingest.py
chunks = legal_chunker.chunk_by_document_type(cleaned_text, doc_type)
```

### 3. **Enhanced Metadata**

Each chunk includes rich metadata:

```python
{
    "section_title": "1.1 COVERAGE",
    "text": "This policy provides coverage for medical expenses...",
    "chunk_id": "section_1_1",
    "metadata": {
        "section_anchor": "1.1",
        "section_type": "numbered_policy_section",
        "word_count": 45,
        "chunking_method": "policy_section"
    }
}
```

## Usage Examples

### Upload Policy Document

```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@policy_document.pdf" \
  -F "doc_type=policy" \
  -F "doc_title=Health Insurance Policy"
```

### Upload Contract Document

```bash
curl -X POST "http://localhost:8000/ingest/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@contract.pdf" \
  -F "doc_type=contract" \
  -F "doc_title=Employment Agreement"
```

### Programmatic Usage

```python
from chunking.chunker import LegalDocumentChunker

chunker = LegalDocumentChunker()

# Policy document chunking
policy_chunks = chunker.chunk_policy_by_section(policy_text)

# Document type-aware chunking
chunks = chunker.chunk_by_document_type(text, doc_type="policy")
```

## Document Type Support

### Policy Documents
- **Types**: `policy`, `insurance_policy`, `health_policy`
- **Method**: Section-based chunking
- **Pattern**: `\d+(\.\d+)?\s+[A-Z][^\n]*`

### Contract Documents
- **Types**: `contract`, `agreement`, `legal_contract`
- **Method**: Legal section chunking
- **Pattern**: `ARTICLE`, `SECTION`, `CLAUSE`

### Generic Documents
- **Types**: `unknown`, `document`, `text`
- **Method**: Sliding window chunking
- **Pattern**: Fixed word count chunks

## Example Policy Document Structure

```
HEALTH INSURANCE POLICY

1.1 COVERAGE
This policy provides coverage for medical expenses incurred by the insured.
Coverage includes hospitalization, outpatient care, and prescription drugs.

1.2 EXCLUSIONS
Pre-existing conditions are excluded from coverage for the first 12 months.
Cosmetic procedures are not covered unless medically necessary.

2.1 DEDUCTIBLE
The annual deductible is $1,000 per individual and $2,000 per family.
The deductible must be met before coverage begins.

2.2 COPAYMENTS
Office visits require a $25 copayment.
Specialist visits require a $40 copayment.
```

### Generated Chunks

1. **Chunk 1**:
   - Title: "1.1 COVERAGE"
   - Anchor: "1.1"
   - Content: Coverage details...

2. **Chunk 2**:
   - Title: "1.2 EXCLUSIONS"
   - Anchor: "1.2"
   - Content: Exclusion details...

3. **Chunk 3**:
   - Title: "2.1 DEDUCTIBLE"
   - Anchor: "2.1"
   - Content: Deductible details...

## Benefits

### 1. **Improved Retrieval Accuracy**
- Section-based chunks provide better context
- Related content stays together
- Easier to find specific policy sections

### 2. **Better User Experience**
- More meaningful search results
- Clear section identification
- Structured document navigation

### 3. **Enhanced Metadata**
- Rich section information
- Better filtering capabilities
- Improved search relevance

### 4. **Automatic Adaptation**
- No manual configuration needed
- Works with existing documents
- Backward compatible

## Configuration

### Custom Section Patterns

You can extend the section detection patterns:

```python
class LegalDocumentChunker:
    def __init__(self):
        self.section_patterns = [
            r'^ARTICLE\s+\d+[\.:]?\s*[A-Z\s]+',
            r'^SECTION\s+\d+[\.:]?\s*[A-Z\s]+',
            r'^\d+\.\s*[A-Z\s]+',  # Standard numbered sections
            r'^[A-Z][A-Z\s]{3,}:',  # All caps headers
            # Add your custom patterns here
        ]
```

### Document Type Mapping

Customize document type to chunking method mapping:

```python
def chunk_by_document_type(self, text: str, doc_type: str):
    if doc_type.lower() in ['policy', 'insurance_policy', 'health_policy']:
        return self.chunk_policy_by_section(text)
    elif doc_type.lower() in ['contract', 'agreement', 'legal_contract']:
        return self.chunk_text(text, preserve_sections=True)
    else:
        return self.chunk_text(text, preserve_sections=False)
```

## Testing

Run the test script to verify functionality:

```bash
python test_policy_chunking.py
```

This will test:
- Policy section detection
- Document type-aware chunking
- Edge cases and error handling
- Integration with metadata builder

## Edge Cases Handled

### 1. **Empty Documents**
- Returns empty chunk list
- Logs appropriate warning

### 2. **No Numbered Sections**
- Falls back to general chunking
- Preserves document content

### 3. **Malformed Sections**
- Handles incomplete section structures
- Preserves available content

### 4. **Mixed Content**
- Handles documents with both structured and unstructured content
- Applies appropriate chunking to each section

## Performance Considerations

### 1. **Processing Speed**
- Regex-based detection is fast
- Minimal overhead compared to general chunking
- Efficient for large documents

### 2. **Memory Usage**
- Processes documents in chunks
- No significant memory increase
- Suitable for production use

### 3. **Scalability**
- Works with documents of any size
- Handles batch processing efficiently
- Integrates with existing pipeline

## Future Enhancements

### 1. **Advanced Section Detection**
- Machine learning-based section identification
- Support for more document formats
- Automatic language detection

### 2. **Custom Section Types**
- User-defined section patterns
- Domain-specific chunking rules
- Configurable chunking strategies

### 3. **Enhanced Metadata**
- Section hierarchy detection
- Cross-reference identification
- Automatic tagging

### 4. **Quality Metrics**
- Chunk quality scoring
- Content completeness analysis
- Section boundary validation

## Troubleshooting

### Common Issues

1. **No Sections Detected**
   - Check document format
   - Verify section numbering pattern
   - Review document type setting

2. **Incorrect Chunking**
   - Validate document structure
   - Check regex patterns
   - Review chunking method selection

3. **Performance Issues**
   - Monitor document size
   - Check regex complexity
   - Review chunking parameters

### Debug Mode

Enable debug logging to see chunking details:

```python
import logging
logging.getLogger('chunking.chunker').setLevel(logging.DEBUG)
```

## Summary

The Policy Section Chunking feature significantly enhances the Legal RAG System by:

1. **Providing intelligent document segmentation** for policy documents
2. **Automatically detecting numbered sections** and preserving structure
3. **Supporting multiple document types** with appropriate chunking methods
4. **Generating rich metadata** for better search and retrieval
5. **Maintaining backward compatibility** with existing functionality

This integration transforms the system's ability to handle structured legal documents, particularly policy documents, by preserving their natural organization and making them more searchable and retrievable. 