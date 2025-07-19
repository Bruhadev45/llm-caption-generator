import chromadb
from sentence_transformers import SentenceTransformer

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("captions")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def add_caption_to_db(caption, metadata=None):
    embedding = embedder.encode([caption])[0].tolist()
    collection.add(
        embeddings=[embedding],
        documents=[caption],
        metadatas=[metadata or {}],
        ids=[caption]
    )

def search_similar_captions(query, top_k=3):
    embedding = embedder.encode([query])[0].tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=['documents', 'metadatas']
    )
    return results
