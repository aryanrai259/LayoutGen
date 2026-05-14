"""
Master Retriever Module.
Unified interface for:
1. Pattern Retrieval (Inspiration from 17k dataset).
2. Soft Regulations (Semantic Search from PDFs).
3. Hard Rules (Static constraints from JSON).
"""
import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Load Environment
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterRetriever:
    def __init__(self):
        """Initialize Qdrant, Model, and Load Hard Rules."""
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = os.getenv("QDRANT_API_KEY", None)
        self.reg_collection = os.getenv("REGULATIONS_COLLECTION_NAME", "regulations_chunks")
        self.pat_collection = os.getenv("PATTERNS_COLLECTION_NAME", "patterns_resplan")
        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        
        # 1. Connect to AI Resources
        try:
            self.client = QdrantClient(url=self.qdrant_url, api_key=self.api_key)
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ MasterRetriever connected to {self.qdrant_url}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI resources: {e}")
            self.client = None
            self.model = None

        # 2. Load Hard Rules
        self.hard_rules = {}
        rules_path = Path(__file__).parent / "table_rules.json"
        if rules_path.exists():
            try:
                with open(rules_path, "r") as f:
                    self.hard_rules = json.load(f)
                logger.info("✅ Hard Rules (table_rules.json) loaded.")
            except Exception as e:
                logger.error(f"⚠️ Error loading table_rules.json: {e}")
        else:
            logger.warning(f"⚠️ table_rules.json not found at {rules_path}")

    def retrieve_patterns(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Finds similar floor plan layouts from the ResPlan dataset.
        """
        if not self.client or not self.model:
            return []

        try:
            vector = self.model.encode(query).tolist()
            
            # Universal Search
            if hasattr(self.client, "search"):
                hits = self.client.search(collection_name=self.pat_collection, query_vector=vector, limit=limit)
            else:
                results = self.client.query_points(collection_name=self.pat_collection, query=vector, limit=limit)
                hits = results.points

            results = []
            for hit in hits:
                payload = hit.payload or {}
                results.append({
                    "id": hit.id,
                    "text": payload.get("text", ""),
                    "room_counts": payload.get("room_counts", {}),
                    "original_index": payload.get("original_index", -1),
                    "score": hit.score
                })
            
            logger.info(f"🔍 Found {len(results)} patterns for '{query}'")
            return results

        except Exception as e:
            logger.error(f"Error retrieving patterns: {e}")
            return []

    def retrieve_soft_rules(self, query: str, limit: int = 5) -> List[str]:
        """
        Finds relevant building laws via semantic search.
        """
        if not self.client or not self.model:
            return []

        try:
            vector = self.model.encode(query).tolist()
            
            if hasattr(self.client, "search"):
                hits = self.client.search(collection_name=self.reg_collection, query_vector=vector, limit=limit)
            else:
                results = self.client.query_points(collection_name=self.reg_collection, query=vector, limit=limit)
                hits = results.points

            rules = []
            for hit in hits:
                payload = hit.payload or {}
                text = payload.get("text", "")
                source = payload.get("source", "Unknown")
                if text:
                    rules.append(f"{text} (Source: {source})")
            
            logger.info(f"⚖️ Found {len(rules)} regulation chunks.")
            return rules

        except Exception as e:
            logger.error(f"Error retrieving regulations: {e}")
            return []

    def get_hard_rules(self, room_type: str) -> Dict[str, Any]:
        """
        Returns static constraints (min width, min area) for a room type.
        """
        if not room_type:
            return {}
        rt = room_type.lower()
        
        # Keyword mapping to JSON keys
        if any(x in rt for x in ["bed", "living", "hall", "dining"]):
            return self.hard_rules.get("habitable_rooms", {})
        elif "kitchen" in rt:
            return self.hard_rules.get("kitchen", {})
        elif "bath" in rt or "toilet" in rt:
            return self.hard_rules.get("bathroom", {})
        elif "stair" in rt:
            return self.hard_rules.get("stairs", {})
        elif "garage" in rt or "parking" in rt:
            return self.hard_rules.get("garage", {})
            
        return {}



# -------------------------------------------------
# 🧪 TEST BLOCK (Run this file directly to test)
# -------------------------------------------------
if __name__ == "__main__":
    print("\n--- 🕵️ TESTING MASTER RETRIEVER ---")
    
    # Initialize
    retriever = MasterRetriever()
    
    # 1. Test Hard Rules (JSON)
    print("\n1. Testing Hard Rules (JSON):")
    kitchen_rules = retriever.get_hard_rules("kitchen")
    if kitchen_rules:
        print(f"   ✅ Found Kitchen Rules: {json.dumps(kitchen_rules, indent=2)}")
    else:
        print("   ❌ No hard rules found for 'kitchen' (Check table_rules.json location)")

    # 2. Test Soft Rules (Regulations RAG)
    print("\n2. Testing Soft Rules (Regulations PDF):")
    regulations = retriever.retrieve_soft_rules("minimum ceiling height")
    if regulations:
        for i, r in enumerate(regulations):
            print(f"   ✅ [Result {i+1}] {r[:100]}...")
    else:
        print("   ⚠️ No regulations found (Check Qdrant 'regulations_chunks')")

    # 3. Test Patterns (Inspiration RAG)
    print("\n3. Testing Patterns (17k Dataset):")
    patterns = retriever.retrieve_patterns("3BHK layout with balcony")
    if patterns:
        for p in patterns:
            print(f"   ✅ Found Pattern ID: {p['id']} (Score: {p['score']:.3f})")
            print(f"      Text: {p['text'][:100]}...")
    else:
        print("   ⚠️ No patterns found (Check Qdrant 'patterns_resplan')")