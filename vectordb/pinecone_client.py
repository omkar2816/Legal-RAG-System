# import pinecone

# pinecone.init(api_key='', environment='us-west1-gcp')

# index = pinecone.Index("legal-doc-index")

# def upsert_embeddings(embeddings, metadata):
#     items = [(str(m['chunk_id']), e, m) for e, m in zip(embeddings, metadata)]
#     index.upsert(vectors=items)

# def query_embedding(query_vector, top_k=5):
#     return index.query(vector=query_vector, top_k=top_k, include_metadata=True)

# vectordb/pinecone_client.py

import pinecone
import os

PINECONE_API_KEY = "pcsk_4HPEvB_KFEx72v6em36YNM4ce7pmWw9scbwUzPZ7zNvNG1yvmisv5u7YEYar6wSDKWs2hr"  # Store in .env
PINECONE_ENV = "us-east-1"          # Example: "us-west4-gcp"

INDEX_NAME = "hackrx"

# Initialize connection
def init_pinecone():
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Create index (if not exists)
def create_index(dimension=1536, metric="cosine"):
    init_pinecone()
    if INDEX_NAME not in pinecone.list_indexes():
        pinecone.create_index(
            name=INDEX_NAME,
            dimension=dimension,
            metric=metric,
            metadata_config={
                "indexed": ["doc_id", "page", "chunk_id"]
            }
        )
        print(f"Index {INDEX_NAME} created.")
    else:
        print(f"Index {INDEX_NAME} already exists.")

# Connect to the index
def get_index():
    init_pinecone()
    return pinecone.Index(INDEX_NAME)