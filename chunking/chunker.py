def sliding_window(text, window_size=500, overlap=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), window_size - overlap):
        chunk = ' '.join(words[i:i+window_size])
        chunks.append(chunk)
    return chunks