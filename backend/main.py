"""
FloorplanAI Main Entry Point.
Orchestrates the pipeline: User Request -> RAG/LLM -> Z3 Solver -> SVG/DXF Output.
"""
import os
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

def generate_floorplan(user_request, output_dir="outputs"):
    """
    Main function to generate a floor plan from user requirements.
    
    Args:
        user_request (dict): Contains 'plot_length', 'plot_width', 'num_bedrooms', etc.
        output_dir (str): Folder to save generated files.
        
    Returns:
        dict: Result status and paths to generated files.
    """
    # 1. Setup Output Directory
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    svg_path = os.path.join(output_dir, f"plan_{timestamp}.svg")
    dxf_path = os.path.join(output_dir, f"plan_{timestamp}.dxf")

    logger.info(f"🚀 Starting Generation for Request: {user_request}")

    try:
        # ---------------------------------------------------------
        # PHASE 1: COMPOSITION (The Brain)
        # ---------------------------------------------------------
        logger.info("🧠 Phase 1: Composing Topology (RAG + LLM)...")
        composer = FusionComposer()
        semantic_layout = composer.compose(user_request)

        # ---------------------------------------------------------
        # PHASE 2: SOLVER (The Math)
        # ---------------------------------------------------------
        logger.info("🧮 Phase 2: Solving Geometry (Z3 Constraint Engine)...")
        # Ensure strict plot limits are respected
        solver = Z3FloorPlanSolver(semantic_layout, enable_grid_snapping=True)
        solution = solver.solve()

        if solution["status"] != "success":
            logger.error(f"❌ Solver Failed: {solution.get('reason', 'Unknown Error')}")
            return {
                "status": "error",
                "message": f"Could not generate layout: {solution.get('reason')}"
            }

        # ---------------------------------------------------------
        # PHASE 3: RENDERING (The Visuals)
        # ---------------------------------------------------------
        logger.info("🎨 Phase 3: Rendering Outputs...")
        
        # A. Visual Presentation (SVG)
        svg_renderer = ArchitecturalRenderer(output_file=svg_path)
        svg_renderer.render(solution)
        
        # B. CAD Export (DXF)
        dxf_renderer = DXFRenderer(output_file=dxf_path)
        dxf_renderer.render(solution)

        logger.info("✅ Generation Complete!")
        return {
            "status": "success",
            "svg_path": svg_path,
            "dxf_path": dxf_path,
            "stats": {
                "rooms": len(solution.get("solution", [])),
                "area": user_request["plot_width"] * user_request["plot_length"]
            }
        }

    except Exception as e:
        logger.exception("🔥 Critical System Error")
        return {"status": "error", "message": str(e)}

# --- CLI Testing Interface ---
if __name__ == "__main__":
    # Test Run
    test_request = {
        "plot_length": 15.0,
        "plot_width": 12.0,
        "num_bedrooms": 2,
        "user_preferences": "Open kitchen, large living area",
        "vaastu_enabled": True,
        "orientation": "N"
    }
    
    result = generate_floorplan(test_request)
    print("\n--- RESULT ---")
    print(result)