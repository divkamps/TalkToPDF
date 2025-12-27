from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
from app.retrieval import search_similar_chunks
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.embeddings import add_chunks
import uuid
import os

client = OpenAI()

from app.chunking import chunk_text

app = FastAPI(title="TalkToPDF")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/pdf/upload")
async def upload_pdf(file: UploadFile = File(...)):
    doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    reader = PdfReader(file_path)

    all_chunks = []

    for page_index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        page_number = page_index + 1

        page_chunks = chunk_text(text)

        for idx, chunk in enumerate(page_chunks):
            all_chunks.append({
                "doc_id": doc_id,
                "page": page_number,
                "chunk_id": f"{page_number}_{idx}",
                "text": chunk
            })

    add_chunks(all_chunks)

    return {
        "doc_id": doc_id,
        "chunks_indexed": len(all_chunks)
    }


@app.post("/pdf/{doc_id}/ask")
async def ask_pdf(doc_id: str, payload: AskRequest):
    query = payload.question.strip()

    if not query:
        return {"error": "Question is required"}

    retrieved_chunks = search_similar_chunks(query)

    if not retrieved_chunks:
        return {
            "answer": "I could not find this information in the document.",
            "citations": []
        }

    context = "\n\n".join(
        f"(Page {c['page']}) {c['text']}"
        for c in retrieved_chunks
    )

    system_prompt = (
        "You are a document question-answering assistant.\n"
        "Answer ONLY using the provided document context.\n"
        "If the answer is not present, say:\n"
        "'I could not find this information in the document.'\n"
        "Do not use outside knowledge."
    )

    user_prompt = f"""
Document Context:
{context}

Question:
{query}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0
    )

    answer = response.choices[0].message.content.strip()

    citations = [
        {
            "page": c["page"],
            "snippet": c["text"][:200]
        }
        for c in retrieved_chunks
    ]

    return {
        "answer": answer,
        "citations": citations
    }
