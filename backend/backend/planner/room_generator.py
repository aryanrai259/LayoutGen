"""
Deterministic Room Generator

Generates standardized room structures based on user requirements.
This replaces the unreliable LLM-generated room names with a proper,
structured approach.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Canonical room type mapping
CANONICAL_ROOM_TYPES = {
    "living": "living",
    "kitchen": "kitchen",
    "dining": "dining",
    "bedroom": "bedroom",
    "master_bedroom": "master_bedroom",
    "kids_bedroom": "kids_bedroom",
    "bathroom": "bathroom",
    "master_bathroom": "master_bathroom",
    "common_bathroom": "common_bathroom",
    "corridor": "circulation",
    "passage": "circulation",
    "circulation": "circulation",
    "balcony": "balcony",
    "pooja": "pooja",
    "study": "study",
    "store": "storage"
}

# Standard room naming convention
def generate_room_id(room_type: str, index: int = 0, is_master: bool = False) -> str:
    """
    Generate standardized room IDs.
    
    Examples:
        - generate_room_id("bedroom", 1, False) -> "Bedroom_1"
        - generate_room_id("bedroom", 0, True) -> "Master_Bedroom"
        - generate_room_id("bathroom", 1, False) -> "Bathroom_Common"
    """
    room_type = room_type.lower().strip()
    
    # Master bedroom special case
    if is_master and "bed" in room_type:
        return "Master_Bedroom"
    
    # Master bathroom special case
    if is_master and "bath" in room_type:
        return "Master_Bathroom"
    
    # Common bathroom
    if "bath" in room_type and not is_master:
        if index == 0:
            return "Bathroom_Common"
        else:
            return f"Bathroom_{index + 1}"
    
    # Standard rooms
    type_map = {
        "living": "Living_Hall",
        "kitchen": "Kitchen",
        "dining": "Dining",
        "bedroom": f"Bedroom_{index + 1}",
        "kids_bedroom": f"Bedroom_{index + 1}",
        "corridor": "Corridor",
        "passage": "Corridor",
        "circulation": "Corridor",
        "balcony": f"Balcony_{index + 1}" if index > 0 else "Balcony",
        "pooja": "Pooja_Room",
        "study": "Study_Room",
        "storage": "Storage"
    }
    
    # Try direct match first
    if room_type in type_map:
        return type_map[room_type]
    
    # Try partial match
    for key, value in type_map.items():
        if key in room_type:
            if isinstance(value, str) and "{index}" not in value:
                return value
            elif isinstance(value, str):
                return value.format(index=index)
    
    # Fallback: capitalize and add index
    base_name = room_type.replace("_", " ").title().replace(" ", "_")
    if index > 0:
        return f"{base_name}_{index + 1}"
    return base_name


def generate_standard_rooms(user_request: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate standardized room list based on user requirements.
    
    Args:
        user_request: User input with num_bedrooms, plot dimensions, etc.
    
    Returns:
        List of standardized room dictionaries
    """
    rooms = []
    num_bedrooms = user_request.get("num_bedrooms", 1)
    num_bathrooms = user_request.get("num_bathrooms", num_bedrooms)  # Default: 1 per bedroom
    has_kitchen = user_request.get("has_kitchen", True)
    has_living = user_request.get("has_living", True)
    has_dining = user_request.get("has_dining", True)
    
    # 1. Living Hall (always present)
    if has_living:
        rooms.append({
            "id": "Living_Hall",
            "type": "living",
            "name": "Living Hall"
        })
    
    # 2. Kitchen (always present)
    if has_kitchen:
        rooms.append({
            "id": "Kitchen",
            "type": "kitchen",
            "name": "Kitchen"
        })
    
    # 3. Dining (if requested)
    if has_dining:
        rooms.append({
            "id": "Dining",
            "type": "dining",
            "name": "Dining"
        })
    
    # 4. Master Bedroom (if num_bedrooms >= 1)
    if num_bedrooms >= 1:
        rooms.append({
            "id": "Master_Bedroom",
            "type": "master_bedroom",
            "name": "Master Bedroom"
        })
        
        # Master Bathroom (if num_bathrooms >= 1)
        if num_bathrooms >= 1:
            rooms.append({
                "id": "Master_Bathroom",
                "type": "master_bathroom",
                "name": "Master Bathroom"
            })
    
    # 5. Additional Bedrooms (Bedroom_2, Bedroom_3, etc.)
    for i in range(1, num_bedrooms):
        rooms.append({
            "id": f"Bedroom_{i + 1}",
            "type": "bedroom",
            "name": f"Bedroom {i + 1}"
        })
    
    # 6. Additional Bathrooms (if more than master)
    for i in range(1, num_bathrooms):
        if i == 1:
            rooms.append({
                "id": "Bathroom_Common",
                "type": "bathroom",
                "name": "Common Bathroom"
            })
        else:
            rooms.append({
                "id": f"Bathroom_{i + 1}",
                "type": "bathroom",
                "name": f"Bathroom {i + 1}"
            })
    
    # 7. Corridor (if more than 2 bedrooms)
    if num_bedrooms >= 2:
        rooms.append({
            "id": "Corridor",
            "type": "circulation",
            "name": "Corridor"
        })
    
    logger.info(f"✅ Generated {len(rooms)} standardized rooms")
    return rooms


def generate_standard_adjacencies(rooms: List[Dict[str, Any]], num_bedrooms: int) -> List[List[str]]:
    """
    Generate standard adjacency relationships based on architectural best practices.
    
    Args:
        rooms: List of room dictionaries
        num_bedrooms: Number of bedrooms
    
    Returns:
        List of adjacency pairs [room_id1, room_id2]
    """
    adjacencies = []
    room_ids = [r["id"] for r in rooms]
    
    # Helper to check if room exists
    def has_room(room_id):
        return room_id in room_ids
    
    # 1. Living Hall connections (hub)
    if has_room("Living_Hall"):
        if has_room("Kitchen"):
            adjacencies.append(["Living_Hall", "Kitchen"])
        if has_room("Dining"):
            adjacencies.append(["Living_Hall", "Dining"])
            if has_room("Kitchen"):
                adjacencies.append(["Dining", "Kitchen"])
        if has_room("Corridor"):
            adjacencies.append(["Living_Hall", "Corridor"])
    
    # 2. Master Bedroom connections
    if has_room("Master_Bedroom"):
        if has_room("Master_Bathroom"):
            adjacencies.append(["Master_Bedroom", "Master_Bathroom"])
        if has_room("Corridor"):
            adjacencies.append(["Master_Bedroom", "Corridor"])
        elif has_room("Living_Hall"):
            # If no corridor, connect directly to living (for 1-2 bedroom layouts)
            adjacencies.append(["Master_Bedroom", "Living_Hall"])
    
    # 3. Additional Bedrooms via Corridor
    if has_room("Corridor"):
        for i in range(2, num_bedrooms + 1):
            bed_id = f"Bedroom_{i}"
            if has_room(bed_id):
                adjacencies.append(["Corridor", bed_id])
    
    # 4. Common Bathroom connections
    if has_room("Bathroom_Common"):
        if has_room("Corridor"):
            adjacencies.append(["Bathroom_Common", "Corridor"])
        elif num_bedrooms == 1:
            # For 1BHK, connect to living
            if has_room("Living_Hall"):
                adjacencies.append(["Bathroom_Common", "Living_Hall"])
    
    # 5. Additional Bathrooms
    for i in range(2, 10):  # Check up to 10 bathrooms
        bath_id = f"Bathroom_{i}"
        if has_room(bath_id):
            # Connect to nearest bedroom or corridor
            bed_id = f"Bedroom_{i}"
            if has_room(bed_id):
                adjacencies.append([bath_id, bed_id])
            elif has_room("Corridor"):
                adjacencies.append([bath_id, "Corridor"])
    
    logger.info(f"✅ Generated {len(adjacencies)} standard adjacencies")
    return adjacencies


def normalize_llm_topology(llm_output: Dict[str, Any], user_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and standardize LLM-generated topology.
    
    This function:
    1. Replaces inconsistent room names with standardized ones
    2. Ensures all required rooms are present
    3. Fixes room types to match canonical types
    4. Validates and fixes adjacencies
    
    Args:
        llm_output: Raw output from LLM topology planner
        user_request: Original user request
    
    Returns:
        Normalized topology with standardized room names and types
    """
    logger.info("🔧 Normalizing LLM topology output...")
    
    # Generate standard rooms (our ground truth)
    standard_rooms = generate_standard_rooms(user_request)
    standard_room_map = {r["id"]: r for r in standard_rooms}
    
    # Create mapping from LLM room names to standard names
    llm_rooms = llm_output.get("rooms", [])
    name_mapping = {}  # Maps LLM room IDs to standard room IDs
    
    # Try to match LLM rooms to standard rooms
    for llm_room in llm_rooms:
        llm_id = llm_room.get("id", "")
        llm_type = llm_room.get("type", "").lower()
        
        # Find matching standard room
        matched = False
        for std_room in standard_rooms:
            std_type = std_room["type"].lower()
            
            # Direct type match
            if llm_type == std_type or llm_type in std_type or std_type in llm_type:
                # Check if it's a master bedroom
                is_master = "master" in llm_id.lower() or "master" in llm_type
                if is_master and "master" in std_type:
                    name_mapping[llm_id] = std_room["id"]
                    matched = True
                    break
                elif not is_master and "master" not in std_type:
                    # Try to match by index if it's a numbered room
                    if "bedroom" in llm_type:
                        # Extract number from LLM ID
                        import re
                        numbers = re.findall(r'\d+', llm_id)
                        if numbers:
                            idx = int(numbers[0]) - 1
                            if idx < len([r for r in standard_rooms if "bedroom" in r["type"].lower()]):
                                name_mapping[llm_id] = std_room["id"]
                                matched = True
                                break
                    else:
                        name_mapping[llm_id] = std_room["id"]
                        matched = True
                        break
        
        # If no match found, try fuzzy matching
        if not matched:
            for std_room in standard_rooms:
                if std_room["id"] not in name_mapping.values():
                    # Fuzzy match by type keywords
                    if any(kw in llm_type for kw in ["living", "hall"]) and "living" in std_room["type"]:
                        name_mapping[llm_id] = std_room["id"]
                        matched = True
                        break
                    elif "kitchen" in llm_type and "kitchen" in std_room["type"]:
                        name_mapping[llm_id] = std_room["id"]
                        matched = True
                        break
                    elif "dining" in llm_type and "dining" in std_room["type"]:
                        name_mapping[llm_id] = std_room["id"]
                        matched = True
                        break
                    elif "bath" in llm_type and "bath" in std_room["type"]:
                        name_mapping[llm_id] = std_room["id"]
                        matched = True
                        break
                    elif ("corridor" in llm_type or "passage" in llm_type or "circulation" in llm_type) and "circulation" in std_room["type"]:
                        name_mapping[llm_id] = std_room["id"]
                        matched = True
                        break
    
    # Use standard rooms (replace LLM rooms entirely)
    normalized_rooms = standard_rooms.copy()
    
    # Normalize adjacencies
    llm_adjacencies = llm_output.get("adjacencies", [])
    normalized_adjacencies = []
    
    for adj in llm_adjacencies:
        if len(adj) >= 2:
            room1, room2 = adj[0], adj[1]
            # Map to standard names
            room1_std = name_mapping.get(room1, room1)
            room2_std = name_mapping.get(room2, room2)
            
            # Only add if both rooms exist in standard rooms
            if room1_std in [r["id"] for r in normalized_rooms] and room2_std in [r["id"] for r in normalized_rooms]:
                if [room1_std, room2_std] not in normalized_adjacencies and [room2_std, room1_std] not in normalized_adjacencies:
                    normalized_adjacencies.append([room1_std, room2_std])
    
    # If LLM adjacencies are poor, use standard adjacencies
    if len(normalized_adjacencies) < len(normalized_rooms) - 1:
        logger.warning("⚠️ LLM adjacencies insufficient, using standard adjacencies")
        normalized_adjacencies = generate_standard_adjacencies(
            normalized_rooms,
            user_request.get("num_bedrooms", 1)
        )
    
    logger.info(f"✅ Normalized: {len(normalized_rooms)} rooms, {len(normalized_adjacencies)} adjacencies")
    
    return {
        "rooms": normalized_rooms,
        "adjacencies": normalized_adjacencies,
        "reasoning": f"Normalized from LLM output. Original had {len(llm_rooms)} rooms."
    }

