"""
LLM Topology Planner (Structured Version).

Uses deterministic room generation with LLM-assisted adjacency optimization.
This ensures consistent, standardized room names and types.
"""
import os
import json
import logging
import re
from typing import Dict, List, Any
from groq import Groq

# Import deterministic room generator
from backend.planner.room_generator import (
    generate_standard_rooms,
    generate_standard_adjacencies,
    normalize_llm_topology
)

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMTopologyPlanner:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not found. Using deterministic topology only.")
            self.client = None
            return
        
        try:
            self.client = Groq(api_key=api_key)
            self.model_name = "llama-3.3-70b-versatile" 
            logger.info(f"✅ LLM Topology Planner initialized (Structured Mode)")
        except Exception as e:
            logger.error(f"Failed to initialize Groq: {e}")
            self.client = None
        
    def plan_topology(self, user_request, rag_patterns, vaastu_rules):
        """
        Generates topology using hybrid approach:
        1. Get base rooms deterministically
        2. Inject Entrance if missing
        3. Use LLM to generate adjacencies only
        4. Return standardized structure
        """
        # STEP 1: Get base rooms (deterministic)
        standard_rooms = generate_standard_rooms(user_request)
        
        # STEP 2: Inject Entrance if missing
        entrance_exists = any(r.get("id", "").lower() == "entrance" or r.get("type", "").lower() == "entrance" 
                             for r in standard_rooms)
        if not entrance_exists:
            entrance_room = {
                "id": "Entrance",
                "type": "entrance",
                "name": "Entrance",
                "legal": {
                    "min_area": 4.0,
                    "min_width": 2.0,
                    "min_height": 2.0
                }
            }
            standard_rooms.append(entrance_room)
            logger.info("✅ Injected Entrance room")
        
        # STEP 3: Get base adjacencies (including Entrance -> Living_Hall)
        standard_adjacencies = generate_standard_adjacencies(
            standard_rooms,
            user_request.get("num_bedrooms", 1)
        )
        
        # Ensure Entrance -> Living_Hall connection exists
        entrance_to_living = ["Entrance", "Living_Hall"]
        if entrance_to_living not in standard_adjacencies and [entrance_to_living[1], entrance_to_living[0]] not in standard_adjacencies:
            standard_adjacencies.append(entrance_to_living)
            logger.info("✅ Added Entrance -> Living_Hall adjacency")
        
        # STEP 4: If LLM available, try to optimize adjacencies
        if self.client:
            try:
                optimized_adjacencies = self._optimize_adjacencies_with_llm(
                    standard_rooms,
                    standard_adjacencies,
                    user_request,
                    rag_patterns,
                    vaastu_rules
                )
                if optimized_adjacencies:
                    standard_adjacencies = optimized_adjacencies
                    logger.info("✅ LLM optimized adjacencies")
            except Exception as e:
                logger.warning(f"⚠️ LLM optimization failed, using standard adjacencies: {e}")
        
        # STEP 5: Return standardized structure
        return {
            "rooms": standard_rooms,
            "adjacencies": standard_adjacencies,
            "reasoning": "Hybrid topology: deterministic rooms + LLM adjacencies"
        }

    def _optimize_adjacencies_with_llm(
        self,
        standard_rooms: List[Dict[str, Any]],
        base_adjacencies: List[List[str]],
        user_request: Dict[str, Any],
        rag_patterns: List[Dict[str, Any]],
        vaastu_rules: Dict[str, Any]
    ) -> List[List[str]]:
        """
        Use LLM to suggest adjacency improvements, but keep room names standardized.
        """
        # Format RAG patterns
        formatted_refs = []
        for i, p in enumerate(rag_patterns[:3]):  # Top 3 only
            ref_str = f"--- Pattern {i+1} ---\n"
            ref_str += f"Description: {p.get('text', '')}\n"
            
            if 'graph' in p and 'edges' in p['graph']:
                connections = p['graph']['edges']
                ref_str += f"BLUEPRINT STRUCTURE: {json.dumps(connections)}\n"
            
            formatted_refs.append(ref_str)

        rag_context = "\n".join(formatted_refs)
        
        # Create room list for LLM (with standard IDs)
        room_list = [f"{r['id']} ({r['type']})" for r in standard_rooms]
        
        system_prompt = """You are an Expert Architect specializing in room adjacency optimization.

CRITICAL RULES:
1. You MUST use ONLY the room IDs provided in the STANDARD_ROOMS list
2. Do NOT create new room names or IDs
3. Your job is ONLY to suggest optimal adjacencies between the provided rooms
4. Follow architectural best practices and the reference patterns
5. **MANDATORY**: You MUST connect 'Entrance' to 'Living_Hall'. 'Entrance' implies the main door location.

OUTPUT FORMAT:
Return ONLY valid JSON with this exact structure:
{
    "adjacencies": [["Room_ID_1", "Room_ID_2"], ["Room_ID_3", "Room_ID_4"], ...]
}

Use ONLY room IDs from the STANDARD_ROOMS list."""

        user_prompt = f"""
STANDARD_ROOMS (USE THESE EXACT IDs):
{json.dumps(room_list, indent=2)}

CURRENT ADJACENCIES:
{json.dumps(base_adjacencies, indent=2)}

USER REQUEST:
{json.dumps(user_request, indent=2)}

REFERENCE PATTERNS:
{rag_context}

TASK:
Suggest optimal adjacencies using ONLY the room IDs from STANDARD_ROOMS.
Consider:
- **MANDATORY**: 'Entrance' MUST connect to 'Living_Hall' (main door location)
- Living Hall should connect to Kitchen, Dining, and Corridor
- Bedrooms should connect via Corridor (not directly to Living)
- Bathrooms should connect to bedrooms or corridor
- Follow reference pattern adjacencies where applicable

Return JSON with "adjacencies" array only.
"""

        try:
            logger.info("🧠 LLM optimizing adjacencies...")
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model_name,
                temperature=0.2,  # Low temperature for consistency
                response_format={"type": "json_object"}
            )
            
            # Parse response
            raw = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                llm_output = json.loads(json_match.group())
                suggested_adjacencies = llm_output.get("adjacencies", [])
                
                # Validate: Ensure all room IDs exist in standard rooms
                valid_room_ids = {r["id"] for r in standard_rooms}
                validated_adjacencies = []
                
                for adj in suggested_adjacencies:
                    if len(adj) >= 2:
                        room1, room2 = adj[0], adj[1]
                        # Check if both rooms exist
                        if room1 in valid_room_ids and room2 in valid_room_ids:
                            # Avoid duplicates
                            if [room1, room2] not in validated_adjacencies and [room2, room1] not in validated_adjacencies:
                                validated_adjacencies.append([room1, room2])
                
                # Trust hybrid output: Accept ANY valid adjacencies from LLM
                if len(validated_adjacencies) > 0:
                    # Ensure Entrance -> Living_Hall exists
                    has_entrance_living = any(
                        (adj[0] == "Entrance" and adj[1] == "Living_Hall") or 
                        (adj[1] == "Entrance" and adj[0] == "Living_Hall")
                        for adj in validated_adjacencies
                    )
                    if not has_entrance_living:
                        validated_adjacencies.append(["Entrance", "Living_Hall"])
                        logger.info("✅ Added mandatory Entrance -> Living_Hall connection")
                    
                    logger.info(f"✅ LLM provided {len(validated_adjacencies)} valid adjacencies")
                    return validated_adjacencies
                else:
                    logger.warning(f"⚠️ LLM returned no valid adjacencies, using base")
                    return None
            else:
                raise ValueError("No JSON found in LLM response")
                
        except Exception as e:
            logger.error(f"LLM adjacency optimization failed: {e}")
            return None

    def _get_fallback_topology(self, user_request, reason):
        """Fallback: Use deterministic room generator"""
        logger.info(f"Using deterministic fallback topology: {reason}")
        rooms = generate_standard_rooms(user_request)
        adjacencies = generate_standard_adjacencies(rooms, user_request.get("num_bedrooms", 1))
        return {
            "rooms": rooms,
            "adjacencies": adjacencies,
            "reasoning": f"Deterministic fallback: {reason}"
        }
