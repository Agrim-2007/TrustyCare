"""
RAG Ingestion Pipeline for TrustyBot

Scrapes trustycare.com (with SPA fallback to seed content), chunks text,
generates embeddings using sentence-transformers, and persists a FAISS index.

Usage:
    python rag/ingest.py
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag.seed_content import SEED_CONTENT


# ── Configuration ────────────────────────────────────────────────────────

CHUNK_CONFIG = {
    "chunk_size": 400,
    "chunk_overlap": 80,
    "separators": ["\n\n", "\n", ". ", "? ", "! ", " "],
}

PAGES_TO_SCRAPE = [
    "https://trustycare.com/",
    "https://trustycare.com/about",
    "https://trustycare.com/how-it-works",
    "https://trustycare.com/faq",
    "https://trustycare.com/assessment",
    "https://trustycare.com/blog",
]

VECTORSTORE_DIR = Path(__file__).resolve().parent / "vectorstore"
INGEST_LOG_PATH = Path(__file__).resolve().parent / "ingest_log.json"


# ── Web Scraping ─────────────────────────────────────────────────────────

def scrape_page(url: str) -> str:
    """Attempt to scrape a page. Returns clean text or empty string."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
        if response.status_code != 200:
            print(f"  ⚠ {url} returned status {response.status_code}")
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script, style, nav, footer noise
        for tag in soup(["script", "style", "nav", "footer", "noscript", "svg"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        # Filter out minimal SPA shells (React apps render client-side)
        if len(text) < 200:
            print(f"  ⚠ {url} returned minimal content (SPA shell) — skipping")
            return ""

        return text

    except Exception as e:
        print(f"  ✗ Error scraping {url}: {e}")
        return ""


def scrape_all_pages() -> list[dict]:
    """Scrape all target pages from trustycare.com."""
    scraped = []
    print("\n🌐 Scraping trustycare.com pages...")

    for url in PAGES_TO_SCRAPE:
        print(f"  → {url}")
        text = scrape_page(url)
        if text:
            scraped.append(
                {
                    "content": text,
                    "source_url": url,
                    "page_type": "scraped",
                    "objection_tags": [],
                    "emotional_tags": [],
                }
            )
            time.sleep(1)  # Polite delay

    return scraped


# ── Chunking ─────────────────────────────────────────────────────────────

def chunk_documents(documents: list[dict]) -> list[dict]:
    """Split documents into chunks with metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_CONFIG["chunk_size"],
        chunk_overlap=CHUNK_CONFIG["chunk_overlap"],
        separators=CHUNK_CONFIG["separators"],
    )

    chunks = []
    for doc in documents:
        text_chunks = splitter.split_text(doc["content"].strip())
        for i, chunk_text in enumerate(text_chunks):
            chunks.append(
                {
                    "text": chunk_text,
                    "metadata": {
                        "source_url": doc["source_url"],
                        "page_type": doc["page_type"],
                        "objection_tags": doc.get("objection_tags", []),
                        "emotional_tags": doc.get("emotional_tags", []),
                        "chunk_index": i,
                    },
                }
            )

    return chunks


# ── Embedding & FAISS Index ──────────────────────────────────────────────

def build_faiss_index(chunks: list[dict]):
    """Embed chunks and build FAISS index. Imports here to avoid slow startup."""
    import numpy as np

    try:
        import faiss
    except ImportError:
        print("✗ faiss-cpu not installed. Run: pip install faiss-cpu")
        sys.exit(1)

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("✗ sentence-transformers not installed. Run: pip install sentence-transformers")
        sys.exit(1)

    print("\n🔤 Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = [c["text"] for c in chunks]
    print(f"📐 Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings).astype("float32")

    # Build FAISS index (Inner Product for normalized vectors = cosine similarity)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Save index
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
    index_path = VECTORSTORE_DIR / "trustycare_health.index"
    faiss.write_index(index, str(index_path))
    print(f"💾 FAISS index saved to {index_path}")

    # Save chunk metadata
    metadata_path = VECTORSTORE_DIR / "chunks_metadata.json"
    metadata = [
        {"text": c["text"], "metadata": c["metadata"]}
        for c in chunks
    ]
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"💾 Chunk metadata saved to {metadata_path}")

    return index, metadata


# ── Logging ──────────────────────────────────────────────────────────────

def save_ingest_log(
    scraped_count: int,
    seed_count: int,
    total_chunks: int,
    chunk_config: dict,
):
    """Save ingestion summary to JSON log."""
    log = {
        "timestamp": datetime.now().isoformat(),
        "scraped_pages": scraped_count,
        "seed_documents_used": seed_count,
        "total_chunks": total_chunks,
        "chunk_config": chunk_config,
        "embedding_model": "all-MiniLM-L6-v2",
        "index_type": "FAISS IndexFlatIP (cosine)",
        "vectorstore_path": str(VECTORSTORE_DIR),
    }
    with open(INGEST_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)
    print(f"📋 Ingest log saved to {INGEST_LOG_PATH}")


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🚀 TrustyBot RAG Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Try scraping
    scraped = scrape_all_pages()
    scraped_count = len(scraped)

    # Step 2: Always use seed content (authoritative source of truth)
    print(f"\n📚 Loading {len(SEED_CONTENT)} seed documents (authoritative content)...")
    all_documents = SEED_CONTENT.copy()

    # Add any successfully scraped pages
    if scraped:
        print(f"✓ Adding {scraped_count} scraped pages to knowledge base")
        all_documents.extend(scraped)
    else:
        print("ℹ No pages scraped (SPA). Using seed content exclusively.")

    # Step 3: Chunk
    print(f"\n✂️  Chunking {len(all_documents)} documents...")
    chunks = chunk_documents(all_documents)
    print(f"   → {len(chunks)} chunks created")

    # Step 4: Embed + index
    build_faiss_index(chunks)

    # Step 5: Log
    save_ingest_log(
        scraped_count=scraped_count,
        seed_count=len(SEED_CONTENT),
        total_chunks=len(chunks),
        chunk_config=CHUNK_CONFIG,
    )

    print("\n" + "=" * 60)
    print(f"✅ Ingestion complete! {len(chunks)} chunks indexed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
