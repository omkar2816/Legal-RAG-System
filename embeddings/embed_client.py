from openai import OpenAIEmbeddings  # or use HuggingFace/SentenceTransformers

def get_embeddings(text_list, model="text-embedding-ada-002"):
    import openai
    openai.api_key = 'your-key'
    response = openai.Embedding.create(
        input=text_list,
        model=model
    )
    return [d['embedding'] for d in response['data']]