import sys
import os

# Ensure project root is on PYTHONPATH so we can import 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# CORRECTION 1: Import the 'settings' object, not just the module
from backend.config import settings

from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

# CORRECTION 2: Handle API Key gracefully (if you added it to config later)
client = QdrantClient(
    url=settings.QDRANT_URL,
    # If you aren't using an API key locally, this can be omitted or left as None
    api_key=None 
)

# CORRECTION 3: Use the exact variable names from your backend/config.py
collections = [
    settings.REGULATIONS_COLLECTION_NAME,
    settings.PATTERNS_COLLECTION_NAME,
]

print(f"Connecting to Qdrant at {settings.QDRANT_URL}...")

for name in collections:
    # This method works if you have qdrant-client >= 1.7.0
    if client.collection_exists(name):
        print(f"✓ Collection already exists: {name}")
    else:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                # CORRECTION 4: Use VECTOR_SIZE (384) as defined in config
                size=settings.VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"✓ Created collection: {name}")

if __name__ == "__main__":
    print("✨ Collection initialization complete.")