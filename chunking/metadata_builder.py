def build_metadata(chunks, doc_id):
    metadata = []
    for i, chunk in enumerate(chunks):
        metadata.append({
            "doc_id": doc_id,
            "chunk_id": i,
            "content": chunk
        })
    return metadata