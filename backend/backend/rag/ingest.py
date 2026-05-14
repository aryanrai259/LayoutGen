"""
Master Ingestion Script (Fixed for Mixed Data Types).
1. Regulations: Extracts text while preserving Table layouts.
2. Patterns: robustness check to skip non-geometry data (strings/ints).
"""
import os
import pickle
import glob
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import pdfplumber
from shapely.geometry import MultiPolygon, Polygon

# --- CONFIGURATION ---
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_KEY = os.getenv("QDRANT_API_KEY", None)
REG_COLLECTION = os.getenv("REGULATIONS_COLLECTION_NAME", "regulations_chunks")
PAT_COLLECTION = os.getenv("PATTERNS_COLLECTION_NAME", "patterns_resplan")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
VECTOR_SIZE = 384

# Paths
SOURCE_REG_DIR = Path(__file__).parent / "regulations" / "sources"
PATTERN_FILE = Path("backend/rag/patterns/datasets/ResPlan.pkl") 
# ^ Updated to your correct path

# Limit patterns for testing (set to None for all 17,000)
PATTERN_LIMIT = 500 

def count_rooms(geometry_obj):
    """Helper to count rooms inside a Shapely object."""
    # FAILSAFE: If it's a string, int, or random data, return 0
    if not hasattr(geometry_obj, "is_empty"):
        return 0
        
    if geometry_obj is None or geometry_obj.is_empty:
        return 0
    if isinstance(geometry_obj, MultiPolygon):
        return len(geometry_obj.geoms) # Count individual shapes
    if isinstance(geometry_obj, Polygon):
        return 1
    return 0

def ingest():
    print("--- 🚀 Starting Master Ingestion (Final Fix) ---")
    
    # 1. Connect
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_KEY)
        model = SentenceTransformer(EMBED_MODEL)
        print(f"✅ Connected to Qdrant & Loaded Model: {EMBED_MODEL}")
    except Exception as e:
        print(f"❌ Setup Failed: {e}")
        return

    # 2. Reset Collections
    print("\n--- ♻️  Resetting Collections ---")
    for name in [REG_COLLECTION, PAT_COLLECTION]:
        if client.collection_exists(name):
             client.delete_collection(name)
             
        client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE)
        )
        print(f"   ✨ Re-created: {name}")

    # ==========================================
    # STEP 3: PROCESS REAL PATTERNS (The .pkl)
    # ==========================================
    print(f"\n--- 🧠 Processing Dataset: {PATTERN_FILE} ---")
    if not PATTERN_FILE.exists():
        print(f"❌ Pattern file not found at: {PATTERN_FILE}")
        print("   Please check the path inside ingest.py")
    else:
        try:
            with open(PATTERN_FILE, "rb") as f:
                data = pickle.load(f)
            
            print(f"   📂 Loaded {len(data)} layouts. Processing first {PATTERN_LIMIT if PATTERN_LIMIT else 'ALL'}...")
            
            points = []
            valid_count = 0
            
            for i, layout in enumerate(data):
                if PATTERN_LIMIT and i >= PATTERN_LIMIT:
                    break
                
                # Dynamic Analysis of the Layout
                room_counts = {}
                for room_type, geom in layout.items():
                    # Only process if we actually found rooms (skips strings/metadata)
                    count = count_rooms(geom)
                    if count > 0:
                        room_counts[room_type] = count
                
                # Only add if we found recognizable rooms
                if room_counts:
                    desc_parts = [f"{count} {r_type}" for r_type, count in room_counts.items()]
                    description = "Residential layout with " + ", ".join(desc_parts) + "."
                    
                    # Metadata
                    meta = {
                        "original_index": i,
                        "room_counts": room_counts,
                        "text": description
                    }
                    
                    # Vectorize
                    vec = model.encode(description).tolist()
                    points.append(models.PointStruct(id=i+1, vector=vec, payload=meta))
                    valid_count += 1
                
                if (i+1) % 100 == 0:
                    print(f"   ... processed {i+1} layouts")

            if points:
                client.upsert(collection_name=PAT_COLLECTION, points=points)
                print(f"✅ Successfully ingested {valid_count} valid patterns.")
            else:
                print("⚠️ No valid patterns found (check data format).")
            
        except Exception as e:
            print(f"❌ Error processing .pkl: {e}")
            import traceback
            traceback.print_exc()

    # ==========================================
    # STEP 4: PROCESS REGULATIONS (PDF Tables)
    # ==========================================
    print("\n--- 📜 Processing Regulations (Table-Aware) ---")
    pdf_files = list(SOURCE_REG_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print("⚠️  No PDFs found.")
    else:
        all_chunks = []
        chunk_id = 0
        
        for pdf_path in pdf_files:
            print(f"   📄 Reading: {pdf_path.name}")
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # layout=True preserves physical location (good for tables)
                    text = page.extract_text(layout=True) or ""
                    
                    # Split by large gaps (paragraphs)
                    chunks = [c.strip() for c in text.split('\n\n') if len(c) > 50]
                    
                    for chunk in chunks:
                        chunk_id += 1
                        vec = model.encode(chunk).tolist()
                        all_chunks.append(models.PointStruct(
                            id=chunk_id,
                            vector=vec,
                            payload={"text": chunk, "source": pdf_path.name}
                        ))

        if all_chunks:
            client.upsert(collection_name=REG_COLLECTION, points=all_chunks)
            print(f"✅ Uploaded {len(all_chunks)} regulation chunks.")

    print("\n🎉 Master Ingestion Complete!")

if __name__ == "__main__":
    ingest()