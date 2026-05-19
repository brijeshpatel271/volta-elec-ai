"""
rag/ingestor.py
Loads engineering documents (PDFs, text, web pages) into ChromaDB vector store.
Supports: PDF, TXT, MD, and direct URL scraping.
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Optional
import requests


# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR       = Path(__file__).parent
DOCUMENTS_DIR  = BASE_DIR / "documents"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
METADATA_FILE  = BASE_DIR / "ingested_docs.json"

DOCUMENTS_DIR.mkdir(exist_ok=True)
VECTORSTORE_DIR.mkdir(exist_ok=True)


# ── Chunking config ────────────────────────────────────────────────────────
CHUNK_SIZE    = 800    # characters per chunk
CHUNK_OVERLAP = 150   # overlap between chunks for context continuity


# ── Free knowledge sources (no login required) ─────────────────────────────
FREE_SOURCES = {
    "Circuit Analysis": [
        {
            "title": "All About Circuits — DC Theory",
            "url": "https://www.allaboutcircuits.com/textbook/direct-current/",
            "type": "web",
            "domain": "Circuit Analysis",
        },
        {
            "title": "All About Circuits — AC Theory",
            "url": "https://www.allaboutcircuits.com/textbook/alternating-current/",
            "type": "web",
            "domain": "Circuit Analysis",
        },
    ],
    "Electronics": [
        {
            "title": "All About Circuits — Semiconductors",
            "url": "https://www.allaboutcircuits.com/textbook/semiconductors/",
            "type": "web",
            "domain": "Electronics",
        },
    ],
    "Digital Systems": [
        {
            "title": "All About Circuits — Digital",
            "url": "https://www.allaboutcircuits.com/textbook/digital/",
            "type": "web",
            "domain": "Digital Systems",
        },
    ],
    "Reference": [
        {
            "title": "NIST Engineering Statistics Handbook",
            "url": "https://www.itl.nist.gov/div898/handbook/",
            "type": "web",
            "domain": "Reference",
        },
    ],
}


def load_metadata() -> dict:
    """Load record of previously ingested documents."""
    if METADATA_FILE.exists():
        with open(METADATA_FILE) as f:
            return json.load(f)
    return {}


def save_metadata(meta: dict) -> None:
    with open(METADATA_FILE, "w") as f:
        json.dump(meta, f, indent=2)


def file_hash(path: Path) -> str:
    """SHA256 hash of a file for change detection."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def chunk_text(text: str, source: str, metadata: dict) -> list[dict]:
    """
    Split text into overlapping chunks with metadata.
    Returns list of {"text": str, "metadata": dict}
    """
    # Clean text
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    text = text.strip()

    chunks = []
    start = 0
    chunk_id = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        # Try to break at sentence boundary
        if end < len(text):
            for punct in [". ", ".\n", "! ", "? ", "\n\n"]:
                boundary = text.rfind(punct, start + CHUNK_SIZE // 2, end)
                if boundary != -1:
                    end = boundary + len(punct)
                    break

        chunk_text_str = text[start:end].strip()
        if len(chunk_text_str) > 50:  # Skip tiny chunks
            chunks.append({
                "text": chunk_text_str,
                "metadata": {
                    **metadata,
                    "chunk_id": chunk_id,
                    "source": source,
                    "char_start": start,
                },
            })
            chunk_id += 1

        start = end - CHUNK_OVERLAP
        if start >= len(text):
            break

    return chunks


def extract_pdf(path: Path) -> str:
    """Extract text from PDF using pypdf (free, no dependencies)."""
    try:
        import pypdf
        reader = pypdf.PdfReader(str(path))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)
    except ImportError:
        # Fallback: pdfminer
        try:
            from pdfminer.high_level import extract_text
            return extract_text(str(path))
        except ImportError:
            return f"[PDF extraction failed — install pypdf: pip install pypdf]"
    except Exception as e:
        return f"[PDF read error: {e}]"


def extract_web(url: str, max_chars: int = 50000) -> str:
    """Scrape text content from a web page."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; VOLTA-EE-Bot/1.0)"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        html = resp.text

        # Basic HTML → text (no BeautifulSoup needed)
        # Remove scripts and styles
        html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL)
        html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL)
        # Convert common tags to newlines
        html = re.sub(r"<(br|p|h[1-6]|li|tr|div)[^>]*>", "\n", html, flags=re.IGNORECASE)
        # Strip remaining tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Decode HTML entities
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace(
            "&gt;", ">").replace("&nbsp;", " ").replace("&#39;", "'").replace(
            "&quot;", '"')
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_chars]
    except Exception as e:
        return f"[Web scrape error for {url}: {e}]"


def ingest_file(path: Path, domain: str = "General") -> list[dict]:
    """Ingest a single file and return chunks."""
    path = Path(path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        text = extract_pdf(path)
    elif ext in [".txt", ".md"]:
        text = path.read_text(encoding="utf-8", errors="ignore")
    else:
        return []

    if not text or text.startswith("["):
        return []

    metadata = {
        "title": path.stem,
        "domain": domain,
        "file": path.name,
        "type": "file",
    }
    return chunk_text(text, str(path), metadata)


def ingest_url(url: str, title: str, domain: str) -> list[dict]:
    """Scrape a URL and return chunks."""
    text = extract_web(url)
    if not text or text.startswith("["):
        return []
    metadata = {
        "title": title,
        "domain": domain,
        "url": url,
        "type": "web",
    }
    return chunk_text(text, url, metadata)


def get_chroma_collection():
    """Initialize and return the ChromaDB collection."""
    try:
        import chromadb
        from chromadb.utils import embedding_functions

        client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))

        # Use sentence-transformers for embeddings (free, local)
        try:
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"  # 80MB, very fast
            )
        except Exception:
            # Fallback to default chromadb embeddings
            ef = embedding_functions.DefaultEmbeddingFunction()

        collection = client.get_or_create_collection(
            name="volta_knowledge",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
        return collection
    except ImportError:
        return None


def add_chunks_to_store(collection, chunks: list[dict]) -> int:
    """Add text chunks to ChromaDB. Returns count added."""
    if not chunks or collection is None:
        return 0

    BATCH_SIZE = 50
    added = 0

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        ids, texts, metas = [], [], []

        for j, chunk in enumerate(batch):
            # Unique ID from source + chunk_id
            uid = hashlib.md5(
                f"{chunk['metadata']['source']}_{chunk['metadata']['chunk_id']}".encode()
            ).hexdigest()
            ids.append(uid)
            texts.append(chunk["text"])
            metas.append({k: str(v) for k, v in chunk["metadata"].items()})

        try:
            collection.upsert(ids=ids, documents=texts, metadatas=metas)
            added += len(batch)
        except Exception as e:
            print(f"Batch error: {e}")

    return added


def query_knowledge(query: str, n_results: int = 5, domain_filter: Optional[str] = None) -> list[dict]:
    """
    Search the knowledge base for relevant chunks.

    Args:
        query: Natural language query
        n_results: Number of results to return
        domain_filter: Optional domain to filter by (e.g. 'Circuit Analysis')

    Returns:
        List of {"text": str, "metadata": dict, "distance": float}
    """
    collection = get_chroma_collection()
    if collection is None:
        return []

    try:
        count = collection.count()
        if count == 0:
            return []

        where = {"domain": domain_filter} if domain_filter else None
        n = min(n_results, count)

        results = collection.query(
            query_texts=[query],
            n_results=n,
            where=where,
        )

        output = []
        for i, doc in enumerate(results["documents"][0]):
            output.append({
                "text": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else 0,
            })
        return output
    except Exception as e:
        print(f"Query error: {e}")
        return []


def get_store_stats() -> dict:
    """Return stats about the current knowledge base."""
    collection = get_chroma_collection()
    if collection is None:
        return {"status": "not_installed", "count": 0, "domains": []}

    try:
        count = collection.count()
        if count == 0:
            return {"status": "empty", "count": 0, "domains": []}

        # Sample metadata to get domains
        sample = collection.get(limit=min(500, count), include=["metadatas"])
        domains = list(set(
            m.get("domain", "Unknown")
            for m in sample["metadatas"]
            if m
        ))
        return {
            "status": "ready",
            "count": count,
            "domains": sorted(domains),
        }
    except Exception:
        return {"status": "error", "count": 0, "domains": []}
