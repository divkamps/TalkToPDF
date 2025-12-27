import faiss
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

VECTOR_DIM = 1536
INDEX_PATH = "vector.index"
META_PATH = "metadata.json"


def embed_query(text: str) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    vector = response.data[0].embedding
    return np.array([vector]).astype("float32")


def load_index_and_metadata():
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH) as f:
        metadata = json.load(f)
    return index, metadata


def search_similar_chunks(query: str, top_k: int = 4):
    index, metadata = load_index_and_metadata()
    query_vector = embed_query(query)

    distances, indices = index.search(query_vector, top_k)

    results = []
    for idx in indices[0]:
        if idx == -1:
            continue
        results.append(metadata[idx])

    return results
