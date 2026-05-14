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
        # ---------------------------------------------------------
        # PHASE 1: COMPOSITION (Architect Agent)
        # ---------------------------------------------------------
        yield {"type": "progress", "stage": 1, "stage_name": "Architect Agent", "text": "Querying Visual RAG and computing Room Adjacency Graph..."}
        
        composer = FusionComposer()
        state.topology = composer.compose(user_request)
        
        yield {"type": "progress", "stage": 1, "stage_name": "Architect Agent", "text": f"Topology drafted: {len(state.topology.get('rooms', []))} rooms planned."}

        # ---------------------------------------------------------
        # PHASE 2: SOLVER (Engineer Agent)
        # ---------------------------------------------------------
        yield {"type": "progress", "stage": 2, "stage_name": "Engineer Agent", "text": "Translating topology into mathematical Z3 constraints..."}
        
        solver = Z3FloorPlanSolver(state.topology, enable_grid_snapping=True)
        
        # We can yield an intermediate solving state
        yield {"type": "progress", "stage": 2, "stage_name": "Engineer Agent", "text": "Z3 Geometry Solver running... (This may take up to 15 seconds)"}
        
        # Blocking call to Z3
        solution = solver.solve()

        if solution["status"] != "success":
            logger.error(f"❌ Solver Failed: {solution.get('reason', 'Unknown Error')}")
            yield {"type": "error", "stage": 5, "stage_name": "Error", "text": f"Math engine failed to pack rooms: {solution.get('reason')}"}
            return

        state.geometry = solution

        # ---------------------------------------------------------
        # PHASE 3: RENDERING (The Visuals)
        # ---------------------------------------------------------
        yield {"type": "progress", "stage": 3, "stage_name": "Renderer", "text": "Drawing vector blueprint..."}
        
        # A. Visual Presentation (SVG)
        svg_renderer = ArchitecturalRenderer(output_file=svg_path)
        svg_renderer.render(state.geometry)
        
        # B. CAD Export (DXF)
        dxf_renderer = DXFRenderer(output_file=dxf_path)
        dxf_renderer.render(state.geometry)

        # Yield the drafted SVG back to the client!
        try:
            with open(svg_path, "r") as f:
                svg_content = f.read()
            yield {"type": "svg", "svg": svg_content, "is_final": False, "label": "Draft Layout"}
        except Exception as e:
            logger.error(f"Failed to read SVG: {e}")

        # ---------------------------------------------------------
        # PHASE 4: FINAL REFINEMENT
        # ---------------------------------------------------------
        yield {"type": "progress", "stage": 4, "stage_name": "Evaluation", "text": "Applying final quality checks..."}
        
        # Final SVG
        yield {"type": "svg", "svg": svg_content, "is_final": True, "label": "Final Engineered Layout"}
        
        yield {
            "type": "final",
            "text": "Agentic Generation Complete!",
            "metadata": {
                "confidence": 0.92,
                "bylaws_used": ["BBMP 2003", "Vaastu Shastra"],
                "rooms_placed": len(solution.get("solution", []))
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