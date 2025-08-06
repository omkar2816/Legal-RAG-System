# vectordb/pinecone_client.py

import os
from pinecone import Pinecone, ServerlessSpec, CloudProvider
from config.settings import settings

# Global Pinecone client instance
_pc = None

# Initialize connection
def init_pinecone():
    global _pc
    if _pc is None:
        _pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    return _pc

# Create index (if not exists)
def create_index(dimension=None, metric="cosine"):
    if dimension is None:
        dimension = settings.PINECONE_DIMENSION
    
    pc = init_pinecone()
    
    # Check if index exists
    existing_indexes = pc.list_indexes().names()
    
    if settings.PINECONE_INDEX_NAME not in existing_indexes:
        # Create serverless index
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud=CloudProvider.AWS,
                region=settings.PINECONE_ENVIRONMENT
            )
        )
        print(f"Index {settings.PINECONE_INDEX_NAME} created.")
    else:
        print(f"Index {settings.PINECONE_INDEX_NAME} already exists.")

# Connect to the index
def get_index():
    pc = init_pinecone()
    return pc.Index(settings.PINECONE_INDEX_NAME)

# Check metadata size
def check_metadata_size(metadata):
    """
    Check if metadata size is within Pinecone limits
    
    Args:
        metadata: Metadata dictionary
    
    Returns:
        Tuple of (is_valid, size_in_bytes)
    """
    import json
    
    # Convert to JSON to estimate size
    metadata_json = json.dumps(metadata)
    size_bytes = len(metadata_json.encode('utf-8'))  # More accurate size calculation
    
    # Pinecone limit is 40KB (40960 bytes) per vector
    return size_bytes <= 40960, size_bytes

# Trim metadata to fit size limits
def trim_metadata(metadata, current_size):
    """
    Trim metadata to fit within Pinecone size limits
    
    Args:
        metadata: Metadata dictionary
        current_size: Current size in bytes
    
    Returns:
        Trimmed metadata dictionary
    """
    import copy
    import json
    
    # Make a copy to avoid modifying the original
    trimmed = copy.deepcopy(metadata)
    
    # Fields to remove in order of priority (least important first)
    fields_to_trim = [
        'legal_terms',
        'section_title',
        'doc_source',
        'doc_category',
        'doc_date',
        'doc_author',
        'timestamp',
        'file_path',
        'file_name',
        'legal_term_count',
        'total_words',
        'content_hash'
    ]
    
    # Fields to truncate if removal doesn't reduce size enough
    fields_to_truncate = {
        'text': 1000,           # Limit text to 1000 chars
        'doc_title': 100,       # Limit title to 100 chars
        'section_content': 500  # Limit section content to 500 chars
    }
    
    # Keep removing fields until size is acceptable
    for field in fields_to_trim:
        if field in trimmed and current_size > 40960:
            del trimmed[field]
            # Recalculate size
            trimmed_json = json.dumps(trimmed)
            current_size = len(trimmed_json.encode('utf-8'))
            print(f"Removed field '{field}', new size: {current_size} bytes")
    
    # If still too large, truncate text fields
    if current_size > 40960:
        for field, max_length in fields_to_truncate.items():
            if field in trimmed and isinstance(trimmed[field], str) and len(trimmed[field]) > max_length:
                trimmed[field] = trimmed[field][:max_length] + "..."
                # Recalculate size
                trimmed_json = json.dumps(trimmed)
                current_size = len(trimmed_json.encode('utf-8'))
                print(f"Truncated field '{field}' to {max_length} chars, new size: {current_size} bytes")
    
    # If still too large after all trimming, keep only essential fields
    if current_size > 40960:
        essential_fields = ['doc_id', 'chunk_id', 'doc_type', 'is_legal_document']
        extreme_trimmed = {k: trimmed[k] for k in essential_fields if k in trimmed}
        trimmed_json = json.dumps(extreme_trimmed)
        current_size = len(trimmed_json.encode('utf-8'))
        print(f"Extreme trimming applied, keeping only essential fields. New size: {current_size} bytes")
        return extreme_trimmed
    
    return trimmed

# Upsert embeddings
def upsert_embeddings(embeddings, metadata_list):
    """
    Upsert embeddings with metadata to Pinecone
    
    Args:
        embeddings: List of embedding vectors
        metadata_list: List of metadata dictionaries
    """
    index = get_index()
    
    # Prepare vectors for upserting
    vectors = []
    skipped = 0
    
    for i, (embedding, metadata) in enumerate(zip(embeddings, metadata_list)):
        # Check metadata size
        is_valid_size, size_bytes = check_metadata_size(metadata)
        
        if not is_valid_size:
            # Try to trim metadata
            trimmed_metadata = trim_metadata(metadata, size_bytes)
            is_valid_size, size_bytes = check_metadata_size(trimmed_metadata)
            
            if is_valid_size:
                # Use trimmed metadata
                vector_id = f"{trimmed_metadata.get('doc_id', 'doc')}_{trimmed_metadata.get('chunk_id', i)}"
                vectors.append((vector_id, embedding, trimmed_metadata))
                print(f"Trimmed metadata for vector {i} from original size to {size_bytes} bytes")
            else:
                # If still too large, create minimal metadata with just essential fields
                minimal_metadata = {
                    'doc_id': metadata.get('doc_id', f'doc_{i}'),
                    'chunk_id': metadata.get('chunk_id', i),
                    'doc_type': metadata.get('doc_type', 'unknown'),
                    'minimal_metadata': True  # Flag to indicate this is minimal metadata
                }
                
                # Verify minimal metadata size
                is_minimal_valid, minimal_size = check_metadata_size(minimal_metadata)
                if is_minimal_valid:
                    vector_id = f"{minimal_metadata['doc_id']}_{minimal_metadata['chunk_id']}"
                    vectors.append((vector_id, embedding, minimal_metadata))
                    print(f"Using minimal metadata for vector {i}, size: {minimal_size} bytes")
                else:
                    # Skip this vector as a last resort
                    skipped += 1
                    print(f"Skipping vector {i} due to metadata size ({size_bytes} bytes) - even minimal metadata is too large")
        else:
            # Metadata size is fine
            vector_id = f"{metadata.get('doc_id', 'doc')}_{metadata.get('chunk_id', i)}"
            vectors.append((vector_id, embedding, metadata))
    
    # Upsert in batches
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
    
    print(f"Upserted {len(vectors)} vectors to Pinecone (skipped {skipped} due to size limits)")

# Query embeddings
def query_embeddings(query_vector, top_k=None, filter_dict=None):
    """
    Query embeddings from Pinecone
    
    Args:
        query_vector: Query embedding vector
        top_k: Number of results to return
        filter_dict: Filter criteria
    
    Returns:
        Query results with metadata
    """
    if top_k is None:
        top_k = settings.TOP_K_RESULTS
    
    index = get_index()
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter=filter_dict
    )
    
    return results.to_dict()

# Get all vectors (for keyword search)
def get_all_vectors(filter_dict=None, limit=10000):
    """
    Get all vectors from Pinecone index (for keyword search)
    
    Args:
        filter_dict: Optional filter criteria
        limit: Maximum number of vectors to retrieve
    
    Returns:
        List of vectors with metadata
    """
    try:
        index = get_index()
        
        # Use fetch to get all vectors
        # First, get index stats to understand the data
        stats = index.describe_index_stats()
        stats_dict = stats.to_dict()
        total_vectors = stats_dict.get('total_vector_count', 0)
        
        if total_vectors == 0:
            return []
        
        # For keyword search, we need to get all vectors
        # Since Pinecone doesn't have a direct "get all" method,
        # we'll use a dummy query to get a large number of results
        # Create a dummy vector of zeros for the query
        dimension = stats_dict.get('dimension', 1024)
        dummy_vector = [0.0] * dimension
        
        # Query with a very high top_k to get most/all vectors
        results = index.query(
            vector=dummy_vector,
            top_k=min(limit, total_vectors),
            include_metadata=True,
            filter=filter_dict
        )
        
        # Convert results to dictionary format
        results_dict = results.to_dict()
        
        if not results_dict or 'matches' not in results_dict:
            return []
        
        # Convert to list format
        vectors = []
        for match in results_dict['matches']:
            vector_data = {
                'id': match.get('id', ''),
                'metadata': match.get('metadata', {}),
                'score': match.get('score', 0.0)
            }
            vectors.append(vector_data)
        
        return vectors
        
    except Exception as e:
        print(f"Error getting all vectors: {str(e)}")
        return []

# Delete vectors by document ID
def delete_by_doc_id(doc_id):
    """
    Delete all vectors for a specific document
    
    Args:
        doc_id: Document ID to delete
    """
    index = get_index()
    index.delete(filter={"doc_id": doc_id})
    print(f"Deleted vectors for document: {doc_id}")

# Get index statistics
def get_index_stats():
    """
    Get statistics about the index
    
    Returns:
        Index statistics
    """
    index = get_index()
    stats = index.describe_index_stats()
    return stats.to_dict()