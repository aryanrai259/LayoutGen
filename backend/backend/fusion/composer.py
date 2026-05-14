"""
Fusion Composer (Phase 4: Connected Brain).
Now uses the REAL Vaastu module (mapper.py + json) instead of hardcoded rules.
"""
import logging
import json
from typing import Dict, Any
import sys
from pathlib import Path

# Import modules
from backend.rag.retriever import MasterRetriever
from backend.planner.llm_topology import LLMTopologyPlanner

# --- NEW: Import your Vaastu Logic ---
sys.path.append(str(Path(__file__).parent.parent)) # Ensure backend is visible
from backend.vaastu.mapper import get_vaastu_zones 

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FusionComposer:
    def __init__(self):
        logger.info("--- 🎵 Initializing Fusion Composer (Phase 4: Vaastu Integrated) ---")
        self.retriever = MasterRetriever()
        self.planner = LLMTopologyPlanner()
        
    def compose(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"📝 Composer received request: {user_request}")
        
        # 1. RAG Retrieval
        query_text = f"{user_request.get('num_bedrooms', 2)}BHK layout {user_request.get('user_preferences', '')}"
        patterns = self.retriever.retrieve_patterns(query_text, limit=3)
        
        # 2. LLM Planning
        logger.info("📐 Asking Groq to design topology...")
        semantic_layout = self.planner.plan_topology(
            user_request=user_request,
            rag_patterns=patterns,
            vaastu_rules={} 
        )
        
        # 3. Data Enrichment
        logger.info("🔗 Injecting Phase 4 constraints (Real Vaastu Rules)...")
        
        # A. Project Metadata
        semantic_layout["project_meta"] = {
            "plot_length": user_request.get("plot_length", 20.0),
            "plot_width": user_request.get("plot_width", 15.0),
            "orientation": user_request.get("orientation", "N"),
            "crs": "EPSG:3857"
        }

        # B. Room Enrichment
        if "rooms" in semantic_layout:
            for room in semantic_layout["rooms"]:
                r_type = room.get("type", "").lower()
                r_id = room.get("id", "").lower()
                
                # Fetch Hard Rules (Size)
                hard_rules = self.retriever.get_hard_rules(r_type)
                room["legal"] = {
                    "min_area": hard_rules.get("min_area_sqm", 5.0),
                    "min_width": hard_rules.get("min_width_m", 1.8),
                    "min_height": hard_rules.get("min_height_m", 2.4),
                }
                
                # --- NEW: Fetch Real Vaastu Rules ---
                # We combine Type + ID to get the best match (e.g., "Master Bedroom")
                search_term = r_id if "master" in r_id else r_type
                
                vaastu_data = get_vaastu_zones(search_term)
                
                room["vaastu"] = {
                    "preferred_zones": vaastu_data.get("preferred", []),
                    "allowed_zones": vaastu_data.get("allowed", []),
                    "forbidden_zones": vaastu_data.get("avoid", [])
                }
                
                logger.info(f"   🔮 Vaastu for {r_id}: Preferred {room['vaastu']['preferred_zones']}")

        logger.info("✅ Phase 4 Composition Complete.")
        return semantic_layout