import os
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
GEOMETRIES_PATH = os.getenv("MSD_GEOMETRIES_PATH", "../geometries.csv")
COLLECTION_NAME = "msd_patterns"

def process_and_ingest():
    print(f"🔌 Connecting to Qdrant at {QDRANT_URL}...")
    client = QdrantClient(url=QDRANT_URL)
    
    # Ensure collection exists
    try:
        client.get_collection(COLLECTION_NAME)
        print(f"📦 Collection '{COLLECTION_NAME}' exists.")
    except:
        print(f"🏗️ Creating collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
    
    print("🧠 Loading Sentence Transformer embedding model...")
    model = SentenceTransformer(os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"))
    
    print(f"📖 Reading 1.1GB CSV in chunks to save memory (this will take a moment)...")
    
    # We aggregate rooms by apartment_id. 
    # To save memory, we only load 3 columns and read in chunks of 100k lines.
    apartment_rooms = {}
    
    # Note: Error handling in case file isn't exactly where we expect
    if not os.path.exists(GEOMETRIES_PATH):
        print(f"❌ Error: {GEOMETRIES_PATH} not found. Please ensure CSVs are in the root folder.")
        return

    chunk_iter = pd.read_csv(GEOMETRIES_PATH, usecols=['apartment_id', 'entity_type', 'entity_subtype'], chunksize=100000)
    
    for i, chunk in enumerate(chunk_iter):
        print(f"   ⏳ Processing chunk {i+1} ({(i+1)*100}k rows)...")
        areas = chunk[chunk['entity_type'] == 'area']
        
        for _, row in areas.iterrows():
            apt_id = str(row['apartment_id'])
            room = str(row['entity_subtype']).lower()
            
            if apt_id not in apartment_rooms:
                apartment_rooms[apt_id] = []
            if room != 'nan':
                apartment_rooms[apt_id].append(room)
                
        # For speed & prototyping, we will cap ingestion at 10,000 distinct floor plan layouts
        if len(apartment_rooms) >= 10000:
            print("🛑 Reached 10,000 apartments. Stopping chunking for rapid prototyping.")
            break

    print(f"🧩 Extracted {len(apartment_rooms)} unique floor plan topologies. Creating embeddings...")
    
    points = []
    for idx, (apt_id, rooms) in enumerate(apartment_rooms.items()):
        # Create a textual description for semantic search (e.g., "Floor plan with 2 living room, 1 kitchen.")
        room_counts = pd.Series(rooms).value_counts().to_dict()
        desc_parts = [f"{count} {room.replace('_', ' ')}" for room, count in room_counts.items()]
        description = f"Floor plan with {', '.join(desc_parts)}."
        
        # Calculate metadata
        num_bedrooms = sum([count for room, count in room_counts.items() if 'bedroom' in room or 'room' in room])
        
        # Generate 384-dimensional vector
        vector = model.encode(description).tolist()
        
        points.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload={
                    "apartment_id": apt_id,
                    "description": description,
                    "num_bedrooms": num_bedrooms,
                    "rooms": rooms,
                    "source": "Swiss Dwellings (MSD)"
                }
            )
        )
        
        # Batch insert every 500 vectors to Qdrant
        if len(points) >= 500:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            print(f"   📤 Inserted {idx} vectors into Qdrant...")
            points = []
            
    # Insert any remaining points
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        
    print("✅ Ingestion complete! The Visual RAG knowledge base is fully loaded.")

if __name__ == "__main__":
    process_and_ingest()
