"""
Patterns ingestion module.
Loads ResPlan dataset and stores layout patterns in Qdrant.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

from config import (
    QDRANT_URL,
    QDRANT_COLLECTION_PATTERNS,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
    RESPLAN_DATASET_PATH
)


class PatternsIngester:
    """
    Ingests ResPlan dataset and stores layout patterns in Qdrant.
    
    Process:
    1. Load ResPlan.pkl
    2. Extract rooms, adjacencies, bounding box for each plan
    3. Convert to semantic text summary for embedding
    4. Store embeddings with structured payload (adjacency, area ratios)
    """
    
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        try:
            self.client.get_collection(QDRANT_COLLECTION_PATTERNS)
        except Exception:
            self.client.create_collection(
                collection_name=QDRANT_COLLECTION_PATTERNS,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
    
    def load_resplan(self, pkl_path: Path) -> List[Dict[str, Any]]:
        """
        Load ResPlan.pkl file.
        
        Expected structure (example):
        {
            'plan_id': '1012',
            'rooms': [
                {'id': 0, 'type': 'living', 'bbox': [x1, y1, x2, y2]},
                {'id': 1, 'type': 'kitchen', 'bbox': [x1, y1, x2, y2]},
                ...
            ],
            'adjacencies': [(0, 1), (1, 2), ...],
            'total_area': 900.0
        }
        """
        if not pkl_path.exists():
            raise FileNotFoundError(f"ResPlan dataset not found: {pkl_path}")
        
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
        
        # Handle different possible structures
        if isinstance(data, dict):
            # Single plan
            return [data]
        elif isinstance(data, list):
            # List of plans
            return data
        else:
            raise ValueError(f"Unexpected ResPlan data structure: {type(data)}")
    
    def plan_to_semantic_text(self, plan: Dict[str, Any]) -> str:
        """
        Convert a plan dictionary to semantic text for embedding.
        
        Example output:
        "Plan 1012: Living adjacent to Kitchen and Dining; Bedroom adjacent to Bathroom; 
         total area 900 sqft. Layout includes 2 bedrooms, 1 kitchen, 1 living room."
        """
        plan_id = plan.get('plan_id', plan.get('id', 'unknown'))
        rooms = plan.get('rooms', [])
        adjacencies = plan.get('adjacencies', plan.get('edges', []))
        total_area = plan.get('total_area', plan.get('area', 0))
        
        # Count room types
        room_types = {}
        for room in rooms:
            room_type = room.get('type', room.get('label', 'unknown'))
            room_types[room_type] = room_types.get(room_type, 0) + 1
        
        # Build adjacency descriptions
        adjacency_descriptions = []
        room_dict = {r.get('id', i): r for i, r in enumerate(rooms)}
        
        for adj in adjacencies:
            if isinstance(adj, (list, tuple)) and len(adj) >= 2:
                room1_id, room2_id = adj[0], adj[1]
                room1 = room_dict.get(room1_id, {})
                room2 = room_dict.get(room2_id, {})
                room1_type = room1.get('type', room1.get('label', 'room'))
                room2_type = room2.get('type', room2.get('label', 'room'))
                adjacency_descriptions.append(f"{room1_type} adjacent to {room2_type}")
        
        # Build semantic text
        parts = [f"Plan {plan_id}:"]
        
        if adjacency_descriptions:
            parts.append("; ".join(adjacency_descriptions[:5]))  # Limit to 5 adjacencies
        
        parts.append(f"total area {total_area:.0f} sqft")
        
        room_summary = ", ".join([f"{count} {rtype}" for rtype, count in room_types.items()])
        if room_summary:
            parts.append(f"Layout includes {room_summary}")
        
        return ". ".join(parts) + "."
    
    def extract_plan_metadata(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured metadata from a plan for payload storage.
        """
        rooms = plan.get('rooms', [])
        adjacencies = plan.get('adjacencies', plan.get('edges', []))
        total_area = plan.get('total_area', plan.get('area', 0))
        
        # Calculate area ratios
        room_areas = {}
        for room in rooms:
            room_type = room.get('type', room.get('label', 'unknown'))
            bbox = room.get('bbox', [])
            if len(bbox) >= 4:
                width = abs(bbox[2] - bbox[0])
                height = abs(bbox[3] - bbox[1])
                area = width * height
                if room_type not in room_areas:
                    room_areas[room_type] = []
                room_areas[room_type].append(area)
        
        # Calculate average area per room type
        area_ratios = {}
        for room_type, areas in room_areas.items():
            avg_area = sum(areas) / len(areas) if areas else 0
            area_ratios[room_type] = {
                "avg_area": avg_area,
                "ratio_to_total": avg_area / total_area if total_area > 0 else 0,
                "count": len(areas)
            }
        
        # Extract bounding box
        bbox = plan.get('bbox', plan.get('bounding_box', None))
        
        return {
            "plan_id": plan.get('plan_id', plan.get('id', 'unknown')),
            "total_area": total_area,
            "num_rooms": len(rooms),
            "num_adjacencies": len(adjacencies),
            "room_types": list(room_areas.keys()),
            "area_ratios": area_ratios,
            "bbox": bbox,
            "adjacencies": adjacencies[:20]  # Limit for storage
        }
    
    def ingest_resplan(self, pkl_path: Path = None) -> int:
        """
        Ingest ResPlan dataset into Qdrant.
        """
        pkl_path = Path(pkl_path) if pkl_path else Path(RESPLAN_DATASET_PATH)
        
        plans = self.load_resplan(pkl_path)
        print(f"Loaded {len(plans)} plans from ResPlan dataset")
        
        points = []
        for plan_idx, plan in enumerate(plans):
            # Generate semantic text
            semantic_text = self.plan_to_semantic_text(plan)
            
            # Extract metadata
            metadata = self.extract_plan_metadata(plan)
            metadata["dataset"] = "ResPlan"
            metadata["semantic_text"] = semantic_text
            
            # Generate embedding
            embedding = self.embedder.encode(semantic_text).tolist()
            
            # Create point
            points.append(PointStruct(
                id=plan_idx,
                vector=embedding,
                payload=metadata
            ))
        
        # Batch upsert
        if points:
            self.client.upsert(
                collection_name=QDRANT_COLLECTION_PATTERNS,
                points=points
            )
        
        print(f"Ingested {len(points)} plans into Qdrant")
        return len(points)


if __name__ == "__main__":
    # Example usage
    ingester = PatternsIngester()
    
    try:
        total = ingester.ingest_resplan()
        print(f"\nTotal plans ingested: {total}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Please ensure ResPlan.pkl is available at: {RESPLAN_DATASET_PATH}")

