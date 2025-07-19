from sentence_transformers import SentenceTransformer, util

# In-memory store: list of (caption, embedding, metadata)
captions_db = []

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def add_caption_to_db(caption, metadata=None):
    embedding = embedder.encode([caption])[0]
    captions_db.append((caption, embedding, metadata or {}))

def search_similar_captions(query, top_k=3, min_score=0.5):
    if not captions_db:
        return {'documents': [[]], 'metadatas': [[]], 'scores': [[]]}
    query_embedding = embedder.encode([query])[0]
    similarities = [
        (caption, meta, float(util.cos_sim(query_embedding, emb)))
        for caption, emb, meta in captions_db
    ]
    # Filter by minimum similarity score
    filtered = [item for item in similarities if item[2] >= min_score]
    top = sorted(filtered, key=lambda x: -x[2])[:top_k]
    documents = [item[0] for item in top]
    metadatas = [item[1] for item in top]
    scores = [item[2] for item in top]
    return {'documents': [documents], 'metadatas': [metadatas], 'scores': [scores]}
