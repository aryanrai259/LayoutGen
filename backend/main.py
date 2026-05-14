"""
FloorplanAI Main Entry Point.
Orchestrates the pipeline: User Request -> RAG/LLM -> Z3 Solver -> SVG/DXF Output.
Now refactored as a generator to stream states to the frontend!
"""
import os
import json
import logging
from datetime import datetime

# Import Backend Modules
from backend.fusion.composer import FusionComposer
from backend.solver.z3_solver import Z3FloorPlanSolver
from backend.renderer.architectural_renderer import ArchitecturalRenderer
from backend.renderer.dxf_renderer import DXFRenderer

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FloorplanAI_Main")

class DesignState:
    """Manages the State Machine loop between Architect and Engineer"""
    def __init__(self, user_request):
        self.request = user_request
        self.topology = None
        self.geometry = None
        self.errors = []
        self.iteration = 0
        self.max_iterations = 3

def generate_floorplan_stream(user_request, output_dir="outputs"):
    """
    Generator function that yields states for Server-Sent Events (SSE).
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    svg_path = os.path.join(output_dir, f"plan_{timestamp}.svg")
    dxf_path = os.path.join(output_dir, f"plan_{timestamp}.dxf")
    
    state = DesignState(user_request)

    logger.info(f"🚀 Starting Agentic Loop for Request: {user_request}")
    yield {"type": "progress", "stage": 0, "stage_name": "Initialization", "text": "Waking up Architect and Engineer Agents..."}

    try:
        from backend.rag.retriever import MasterRetriever
        from backend.evaluator.engine import EvaluationEngine
        
        # Initialize the global Retriever and Critic
        retriever = MasterRetriever()
        critic = EvaluationEngine(hard_rules_retriever=retriever)
        
        while state.iteration < state.max_iterations:
            state.iteration += 1
            logger.info(f"🔄 Starting Iteration {state.iteration}/{state.max_iterations}...")
            
            # ---------------------------------------------------------
            # PHASE 1: COMPOSITION (Architect Agent)
            # ---------------------------------------------------------
            yield {"type": "progress", "stage": 1, "stage_name": "Architect Agent", "text": f"Iteration {state.iteration}: Architect drafting topology..."}
            
            composer = FusionComposer()
            
            # If we have feedback from a previous failure, inject it into the request!
            if state.errors:
                user_request["critic_feedback"] = "\\n".join(state.errors)
                yield {"type": "progress", "stage": 1, "stage_name": "Architect Agent", "text": "Architect is analyzing Critic feedback to fix layout..."}
            
            state.topology = composer.compose(user_request)
            
            # ---------------------------------------------------------
            # PHASE 2: SOLVER (Engineer Agent)
            # ---------------------------------------------------------
            yield {"type": "progress", "stage": 2, "stage_name": "Engineer Agent", "text": "Engineer calculating geometry constraints..."}
            solver = Z3FloorPlanSolver(state.topology, enable_grid_snapping=True)
            solution = solver.solve()

            if solution["status"] != "success":
                logger.error(f"❌ Engineer Failed: {solution.get('reason')}")
                state.errors = [f"Z3 Solver Failed: {solution.get('reason')}"]
                yield {"type": "progress", "stage": 4, "stage_name": "Evaluation", "text": f"Math failed: {solution.get('reason')}. Retrying..."}
                continue # Try again!

            state.geometry = solution

            # ---------------------------------------------------------
            # PHASE 3: EVALUATION (Critic Agent)
            # ---------------------------------------------------------
            yield {"type": "progress", "stage": 4, "stage_name": "Evaluation", "text": "Critic Agent checking BBMP laws and design ratios..."}
            
            evaluation = critic.evaluate(state.geometry)
            
            if evaluation["passed"] or state.iteration == state.max_iterations:
                if evaluation["passed"]:
                    yield {"type": "progress", "stage": 4, "stage_name": "Evaluation", "text": f"Layout Passed! Score: {evaluation['score']*100:.1f}%"}
                else:
                    yield {"type": "progress", "stage": 4, "stage_name": "Evaluation", "text": f"Max iterations reached. Forcing output. Score: {evaluation['score']*100:.1f}%"}
                
                # Exit the loop and render!
                break
            else:
                # We failed, populate errors and loop!
                state.errors = [evaluation["feedback"]]
                yield {"type": "progress", "stage": 4, "stage_name": "Evaluation", "text": f"Critic found errors (Score {evaluation['score']*100:.1f}%). Triggering redesign..."}
                
        # ---------------------------------------------------------
        # PHASE 4: RENDERING (The Visuals)
        # ---------------------------------------------------------
        yield {"type": "progress", "stage": 3, "stage_name": "Renderer", "text": "Drawing vector blueprint..."}
        
        # A. Visual Presentation (SVG)
        svg_renderer = ArchitecturalRenderer(output_file=svg_path)
        svg_renderer.render(state.geometry)
        
        # B. CAD Export (DXF)
        dxf_renderer = DXFRenderer(output_file=dxf_path)
        dxf_renderer.render(state.geometry)

        try:
            with open(svg_path, "r") as f:
                svg_content = f.read()
            yield {"type": "svg", "svg": svg_content, "is_final": False, "label": f"Iteration {state.iteration} Draft"}
        except Exception as e:
            logger.error(f"Failed to read SVG: {e}")

        # Final SVG
        yield {"type": "svg", "svg": svg_content, "is_final": True, "label": "Final Engineered Layout"}
        
        yield {
            "type": "final",
            "text": "Agentic Generation Complete!",
            "metadata": {
                "confidence": evaluation.get("score", 0.9) * 100,
                "bylaws_used": ["BBMP 2003", "Vaastu Shastra"],
                "rooms_placed": len(state.geometry.get("solution", []))
            }
        }

    except Exception as e:
        logger.exception("🔥 Critical System Error")
        yield {"type": "error", "stage": 5, "stage_name": "Fatal Error", "text": str(e)}

# --- CLI Testing Interface ---
if __name__ == "__main__":
    test_request = {
        "plot_length": 15.0,
        "plot_width": 12.0,
        "num_bedrooms": 2,
        "user_preferences": "Open kitchen, large living area",
        "vaastu_enabled": True,
        "orientation": "N"
    }
    
    for event in generate_floorplan_stream(test_request):
        print(event)