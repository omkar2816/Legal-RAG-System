# vectordb/pinecone_client.py

import os
from pinecone import Pinecone, ServerlessSpec
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
                cloud='aws',
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

# Upsert embeddings with metadata
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
    for i, (embedding, metadata) in enumerate(zip(embeddings, metadata_list)):
        vector_id = f"{metadata.get('doc_id', 'doc')}_{metadata.get('chunk_id', i)}"
        vectors.append((vector_id, embedding, metadata))
    
    # Upsert in batches
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
    
    print(f"Upserted {len(vectors)} vectors to Pinecone")

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
    
    return results

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
        total_vectors = stats.get('total_vector_count', 0)
        
        if total_vectors == 0:
            return []
        
        # For keyword search, we need to get all vectors
        # Since Pinecone doesn't have a direct "get all" method,
        # we'll use a dummy query to get a large number of results
        # Create a dummy vector of zeros for the query
        dimension = stats.get('dimension', 1024)
        dummy_vector = [0.0] * dimension
        
        # Query with a very high top_k to get most/all vectors
        results = index.query(
            vector=dummy_vector,
            top_k=min(limit, total_vectors),
            include_metadata=True,
            filter=filter_dict
        )
        
        if not results or 'matches' not in results:
            return []
        
        # Convert to list format
        vectors = []
        for match in results['matches']:
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
    return index.describe_index_stats()