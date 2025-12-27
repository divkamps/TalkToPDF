import faiss
import os
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

VECTOR_DIM = 1536
INDEX_PATH = "vector.index"
META_PATH = "metadata.json"

index = faiss.IndexFlatL2(VECTOR_DIM)
metadata = []


def embed_texts(texts: list[str]) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )

    vectors = [item.embedding for item in response.data]
    return np.array(vectors).astype("float32")


def add_chunks(chunks: list[dict]):
    global index, metadata

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)

    index.add(vectors)
    metadata.extend(chunks)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w") as f:
        json.dump(metadata, f)

    return {
        "chunks_indexed": len(chunks)
    }
