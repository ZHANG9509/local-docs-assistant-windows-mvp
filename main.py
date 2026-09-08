import os
from fastapi import FastAPI, File, UploadFile, Form
import uvicorn
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from llama_cpp import Llama
import tempfile
from typing import List

app = FastAPI(title="Local Docs Assistant - MVP")

# Chroma client (persist to ./chroma_db)
client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db"))
try:
    collection = client.get_or_create_collection(name="docs")
except Exception:
    collection = client.create_collection(name="docs")

# Embedding model (CPU)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# LLM via llama-cpp-python (ensure models/model.gguf exists)
MODEL_PATH = os.environ.get("MODEL_PATH", "models/model.gguf")
if not os.path.exists(MODEL_PATH):
    print(f"Warning: model not found at {MODEL_PATH}. Please download a gguf/ggml model and set MODEL_PATH or place at models/model.gguf")
llm = Llama(model_path=MODEL_PATH) if os.path.exists(MODEL_PATH) else None


def pdf_to_text(bytes_data: bytes) -> str:
    doc = fitz.open(stream=bytes_data, filetype="pdf")
    texts = []
    for page in doc:
        texts.append(page.get_text())
    return "\n".join(texts)


def docx_to_text(bytes_data: bytes) -> str:
    try:
        from docx import Document
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
            f.write(bytes_data)
            tmp = f.name
        doc = Document(tmp)
        paragraphs = [p.text for p in doc.paragraphs]
        os.unlink(tmp)
        return "\n".join(paragraphs)
    except Exception:
        return ""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    data = await file.read()
    filename = file.filename
    lower = filename.lower()
    if lower.endswith(".pdf"):
        text = pdf_to_text(data)
    elif lower.endswith(".docx"):
        text = docx_to_text(data)
    else:
        # try decode as text
        try:
            text = data.decode(errors="ignore")
        except Exception:
            text = ""
    chunks = chunk_text(text)
    if not chunks:
        return {"status": "empty", "message": "no text extracted"}
    embeddings = embed_model.encode(chunks, convert_to_numpy=True)
    ids = [f"{filename}--{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
    # chroma expects python lists
    collection.add(documents=chunks, metadatas=metadatas, ids=ids, embeddings=embeddings.tolist())
    client.persist()
    return {"status": "ok", "chunks": len(chunks)}


@app.post("/query")
async def query(q: str = Form(...)):
    q_emb = embed_model.encode([q], convert_to_numpy=True)
    results = collection.query(query_embeddings=q_emb.tolist(), n_results=4)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    retrieved = "\n\n".join(docs)
    prompt = (
        "You are a helpful document assistant. Use the following retrieved snippets to answer the question. "
        "If the answer cannot be determined from the snippets, reply with '无法确认，请查看原文'.\n\n"
        f"Context:\n{retrieved}\n\nQuestion: {q}\n\nAnswer:" 
    )
    if llm is None:
        return {"answer": "LLM model not available on this host. Please set MODEL_PATH to a local gguf model and restart.", "sources": metas}
    resp = llm(prompt=prompt, max_tokens=256, temperature=0.0)
    text = ""
    try:
        text = resp["choices"][0]["text"]
    except Exception:
        # fallback for different llama-cpp-python versions
        text = resp.get("choices", [{}])[0].get("text", "") if isinstance(resp, dict) else str(resp)
    return {"answer": text.strip(), "sources": metas}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
