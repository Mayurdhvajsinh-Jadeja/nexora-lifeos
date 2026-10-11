from pathlib import Path

import chromadb
import ollama

BACKEND_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BACKEND_DIR / "data" / "docs"
CHROMA_DIR = BACKEND_DIR / "chroma_data"
EMBED_MODEL = "nomic-embed-text"
SUPPORTED = {".md", ".txt", ".pdf", ".docx"}

_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_collection = _client.get_or_create_collection(
    "nexora_docs", metadata={"hnsw:space": "cosine"}
)


def read_file(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in (".md", ".txt"):
        return path.read_text(encoding="utf-8", errors="ignore")
    if ext == ".pdf":
        from pypdf import PdfReader

        return "\n\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    if ext == ".docx":
        from docx import Document

        return "\n\n".join(p.text for p in Document(str(path)).paragraphs)
    return ""


def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    units = []
    for p in paragraphs:
        if len(p) > max_chars:
            units.extend(line for line in p.split("\n") if line.strip())
        else:
            units.append(p)

    chunks, current = [], ""
    for u in units:
        if current and len(current) + len(u) > max_chars:
            chunks.append(current)
            current = u
        else:
            current = f"{current}\n\n{u}" if current else u
    if current:
        chunks.append(current)
    return chunks


def embed(texts: list[str]) -> list[list[float]]:
    res = ollama.embed(model=EMBED_MODEL, input=texts)
    return res["embeddings"]


def ingest_folder(folder: Path = DOCS_DIR) -> list[dict]:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    report = []
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in SUPPORTED:
            continue
        chunks = chunk_text(read_file(path))
        _collection.delete(where={"source": path.name})
        if not chunks:
            report.append({"file": path.name, "chunks": 0})
            continue
        _collection.add(
            ids=[f"{path.name}-{i}" for i in range(len(chunks))],
            documents=chunks,
            embeddings=embed(chunks),
            metadatas=[{"source": path.name}] * len(chunks),
        )
        report.append({"file": path.name, "chunks": len(chunks)})
    return report


def search(query: str, k: int = 4) -> list[dict]:
    total = _collection.count()
    if total == 0:
        return []
    res = _collection.query(
        query_embeddings=embed([query]), n_results=min(k, total)
    )
    return [
        {"text": doc, "source": meta["source"], "distance": round(dist, 3)}
        for doc, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        )
    ]