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