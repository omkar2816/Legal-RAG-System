from fastapi import FastAPI
# from api.routes import ingest, query, admin
from vectordb.pinecone_client import create_index, get_index

# app = FastAPI()

# app.include_router(ingest.router)
# app.include_router(query.router)
# app.include_router(admin.router)

if __name__ == "__main__":
    create_index()
