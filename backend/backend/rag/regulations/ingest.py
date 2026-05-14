import os
import re
from uuid import uuid4

import pdfplumber
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

# IMPORTANT: your config DOES expose `settings`
from backend.config import settings


# -------------------------------------------------
# Initialize Embedding Model and Qdrant Client
# -------------------------------------------------
print("⏳ Loading embedding model (first run may take time)...")
model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=getattr(settings, "QDRANT_API_KEY", None) or None
)


# -------------------------------------------------
# Utility: clean extracted text
# -------------------------------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


# -------------------------------------------------
# Extract + chunk PDF text
# -------------------------------------------------
def extract_chunks_from_pdf(pdf_path: str):
    chunks = []
    doc_name = os.path.basename(pdf_path)

    print(f"📄 Processing: {doc_name}")

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if not page_text:
                continue

            page_text = clean_text(page_text)

            # Split by byelaw-like numbering (e.g., 3.1, 20.4)
            segments = re.split(r"(?=\b\d+\.\d+\b)", page_text)

            for seg in segments:
                seg = seg.strip()

                # Ignore noise / very small fragments
                if len(seg) < 80:
                    continue

                # Lightweight category tagging (optional but useful)
                category = "general"
                lower = seg.lower()
                if "kitchen" in lower:
                    category = "kitchen"
                elif "bath" in lower or "water closet" in lower:
                    category = "bathroom"
                elif "stair" in lower:
                    category = "stairs"
                elif "setback" in lower:
                    category = "setback"
                elif "ventilation" in lower or "window" in lower:
                    category = "ventilation"
                elif "height" in lower:
                    category = "height"

                chunks.append({
                    "text": seg,
                    "metadata": {
                        "doc": doc_name,
                        "page": page_idx,
                        "category": category,
                        "rule_type": "SOFT",      # numeric rules go to table_rules.json
                        "tags": ["regulations", "bbmp", category]
                    }
                })

    print(f"   → Extracted {len(chunks)} chunks")
    return chunks


# -------------------------------------------------
# Main ingestion pipeline
# -------------------------------------------------
def ingest_regulations():
    pdf_dir = settings.PDF_SOURCE_DIR

    if not os.path.exists(pdf_dir):
        raise FileNotFoundError(f"PDF source directory not found: {pdf_dir}")

    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    if not pdf_files:
        raise RuntimeError("No PDF files found in regulations source directory")

    all_points = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        chunks = extract_chunks_from_pdf(pdf_path)

        if not chunks:
            continue

        texts = [c["text"] for c in chunks]

        # Normalize embeddings for cosine similarity
        embeddings = model.encode(
            texts,
            normalize_embeddings=True
        ).tolist()

        # Optional sanity check
        assert len(embeddings[0]) == settings.VECTOR_SIZE, \
            "Embedding dimension mismatch with Qdrant collection"

        for i, chunk in enumerate(chunks):
            all_points.append(
                models.PointStruct(
                    id=str(uuid4()),
                    vector=embeddings[i],
                    payload={
                        "text": chunk["text"],
                        **chunk["metadata"]
                    }
                )
            )

    if not all_points:
        raise RuntimeError("No valid chunks extracted from PDFs")

    print(f"🚀 Uploading {len(all_points)} chunks to Qdrant...")
    client.upsert(
        collection_name=settings.REGULATIONS_COLLECTION_NAME,
        points=all_points
    )

    print("✅ Regulations ingestion completed successfully!")


# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    ingest_regulations()
