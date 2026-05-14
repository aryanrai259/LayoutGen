"""
Evaluation Engine (Phase 4: The Critic Agent).
Calculates multidimensional scores (Compliance, Design, Vaastu).
Provides feedback to the Architect Agent if the layout fails checks.
"""
import logging
import math
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationEngine:
    def __init__(self, hard_rules_retriever=None):
        """
        Takes the MasterRetriever instance to look up legal limits.
        """
        self.retriever = hard_rules_retriever
        self.target_golden_ratio = 1.618

    def evaluate(self, layout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates the geometry and returns scores + error text.
        """
        logger.info("⚖️ Critic Agent: Evaluating Floor Plan...")
        
        rooms = layout.get("solution", [])
        if not rooms:
            return {"score": 0, "passed": False, "feedback": "No rooms generated."}
        
        errors = []
        
        # 1. Compliance Score (40%)
        compliance_score, compliance_errors = self._check_compliance(rooms)
        errors.extend(compliance_errors)
        
        # 2. Design Score (40%)
        design_score, design_errors = self._check_design(rooms)
        errors.extend(design_errors)
        
        # 3. Vaastu / Soft Score (20%)
        vaastu_score = self._check_vaastu(rooms)
        
        # Total Weighted Score
        total_score = (compliance_score * 0.4) + (design_score * 0.4) + (vaastu_score * 0.2)
        
        passed = len(compliance_errors) == 0 and total_score >= 0.75
        
        logger.info(f"📊 Final Score: {total_score*100:.1f}% | Passed: {passed}")
        
        feedback_str = ""
        if errors:
            feedback_str = "CRITICAL ERRORS FOUND:\n" + "\n".join([f"- {e}" for e in errors])
            logger.warning(feedback_str)
            
        return {
            "score": total_score,
            "passed": passed,
            "feedback": feedback_str,
            "metrics": {
                "compliance": compliance_score,
                "design": design_score,
                "vaastu": vaastu_score
            }
        }

    def _check_compliance(self, rooms: List[Dict[str, Any]]):
        score = 1.0
        errors = []
        
        for room in rooms:
            rid = room.get("id", "")
            rtype = room.get("type", "").lower()
            geo = room.get("geometry", {})
            w, h = geo.get("width", 0), geo.get("height", 0)
            area = w * h
            
            # Fetch Hard Rules via Retriever
            legal = {}
            if self.retriever:
                legal = self.retriever.get_hard_rules(rtype)
            
            min_area = legal.get("min_area_sqm", 4.0)
            min_width = legal.get("min_width_m", 1.5)
            
            # If it's a corridor or bath, thresholds are lower (handled by table_rules.json)
            if area < min_area:
                score -= 0.1
                errors.append(f"{rid} area ({area:.1f}m²) is below legal minimum ({min_area}m²).")
                
            if w < min_width and h < min_width:
                score -= 0.1
                errors.append(f"{rid} is too narrow ({min(w,h):.1f}m). Must be at least {min_width}m.")
                
        return max(0.0, score), errors

    def _check_design(self, rooms: List[Dict[str, Any]]):
        score = 1.0
        errors = []
        
        # Golden Ratio Check
        gr_penalties = 0
        for room in rooms:
            geo = room.get("geometry", {})
            w, h = geo.get("width", 1), geo.get("height", 1)
            ratio = max(w, h) / max(0.1, min(w, h))
            
            # If ratio > 1.7 (Golden Ratio is 1.618), it's a "bowling alley" (bad design) unless it's a corridor
            is_corridor = "circulation" in room.get("type", "").lower() or "corridor" in room.get("id", "").lower()
            if ratio > 1.7 and not is_corridor:
                gr_penalties += 1
                errors.append(f"{room['id']} proportion is too extreme (1:{ratio:.1f}). Force a more square shape closer to 1:1.618.")
                
        score -= (gr_penalties * 0.1)
        
        return max(0.0, score), errors

    def _check_vaastu(self, rooms: List[Dict[str, Any]]):
        # We assume Z3 geometry solver handled Vaastu magnetic pulls, 
        # so this is a simplified 1.0 for now.
        return 1.0
