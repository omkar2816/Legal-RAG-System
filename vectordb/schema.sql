CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    doc_id TEXT,
    chunk_id INTEGER,
    content TEXT,
    metadata JSONB
);