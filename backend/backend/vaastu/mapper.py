import json
import os
from typing import Dict, List

# Load Vaastu Rules
RULES_PATH = os.path.join(os.path.dirname(__file__), "vaastu_rules.json")

try:
    with open(RULES_PATH, "r") as f:
        VAASTU_RULES = json.load(f)
except FileNotFoundError:
    print(f"⚠️ WARNING: {RULES_PATH} not found. Vaastu rules disabled.")
    VAASTU_RULES = {}

def get_vaastu_zones(room_type: str) -> Dict[str, List[str]]:
    """
    Returns preferred/allowed/avoid zones for a given room type.
    Input: "Master Bedroom" -> Output: { "preferred": ["SW"], ... }
    """
    if not room_type:
        return {"preferred": [], "allowed": [], "avoid": []}

    rt = room_type.lower().strip()
    
    # 1. Direct Match (Best Case)
    # e.g., if user asks for "master_bedroom", it matches JSON key directly
    if rt in VAASTU_RULES:
        return VAASTU_RULES[rt]

    # 2. Fuzzy / Keyword Match (Fallback)
    # Maps user input variations to our JSON keys
    key = "living" # Default fallback
    
    if "master" in rt: 
        key = "master_bedroom"
    elif "kid" in rt or "child" in rt: 
        key = "kids_bedroom"
    elif "bed" in rt: 
        key = "bedroom" # General bedroom
    elif "kitchen" in rt: 
        key = "kitchen"
    elif "bath" in rt or "toilet" in rt or "wc" in rt: 
        key = "bathroom"
    elif "living" in rt or "hall" in rt or "lounge" in rt: 
        key = "living"
    elif "dining" in rt: 
        key = "dining"
    elif "pooja" in rt or "puja" in rt or "prayer" in rt: 
        key = "pooja"
    elif "study" in rt or "office" in rt: 
        key = "study"
    elif "entrance" in rt or "main door" in rt: 
        key = "entrance"

    # Return the rule for the matched key, or empty if totally unknown
    return VAASTU_RULES.get(key, {
        "preferred": [], 
        "allowed": [], 
        "avoid": []
    })

# --- Local Test ---
if __name__ == "__main__":
    print("--- Testing Vaastu Mapper ---")
    
    test_rooms = ["Master Bedroom", "Kitchen", "Kids Room", "Toilet", "Meditation Room"]
    
    for room in test_rooms:
        zones = get_vaastu_zones(room)
        print(f"\n🏠 {room}:")
        print(f"   ✅ Preferred: {zones.get('preferred')}")
        print(f"   ⚠️ Allowed:   {zones.get('allowed')}")
        print(f"   ❌ Avoid:     {zones.get('avoid')}")