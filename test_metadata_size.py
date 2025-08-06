from vectordb.pinecone_client import check_metadata_size, trim_metadata
import json

# Create a test metadata with large text content
metadata = {
    'doc_id': 'test_doc',
    'chunk_id': 'chunk_1',
    'chunk_idx': 1,
    'word_count': 500,
    'timestamp': '2023-08-05',
    'section_title': 'A very long section title that exceeds the 50 character limit we set earlier',
    'section_idx': 1,
    'doc_type': 'policy',
    'doc_title': 'Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1',
    'legal_terms': ['hereby', 'whereas', 'agreement', 'jurisdiction', 'governing law', 'dispute resolution', 'arbitration', 'breach', 'termination', 'liability'],
    'legal_density': 0.05,
    'is_legal_document': True,
    'file_size_kb': 450,
    'upload_date': '2023-08-05',
    'total_words': 5000,
    'text': 'A very long text content ' * 1000
}

# Check original metadata size
is_valid, size = check_metadata_size(metadata)
print(f'Original metadata size: {size} bytes, Valid: {is_valid}')

# If too large, trim it
if not is_valid:
    trimmed = trim_metadata(metadata, size)
    is_valid, size = check_metadata_size(trimmed)
    print(f'Trimmed metadata size: {size} bytes, Valid: {is_valid}')
    print(f'Trimmed fields: {list(set(metadata.keys()) - set(trimmed.keys()))}')
    print(f'Remaining fields: {list(trimmed.keys())}')