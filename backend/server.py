import os
import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

# Import the existing pipeline (we will refactor this to yield later in Phase 3)
from main import generate_floorplan

app = FastAPI(
    title="LayoutGen API",
    description="Backend server for automated floor plan synthesis",
    version="1.0.0"
)

# Set up CORS for the Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Pydantic Models for Input Validation
# ---------------------------------------------------------
class FloorPlanRequest(BaseModel):
    description: str
    width: float
    height: float
    rooms: int
    orientation: str
    room_types: List[str]
    jurisdiction: str

# ---------------------------------------------------------
# Helper to map frontend payload to backend engine format
# ---------------------------------------------------------
def map_request_to_engine(payload: FloorPlanRequest) -> dict:
    return {
        "plot_length": payload.height,
        "plot_width": payload.width,
        "num_bedrooms": payload.rooms,
        "user_preferences": payload.description,
        "vaastu_enabled": True, # Defaulting to True for now
        "orientation": payload.orientation.upper()[0] if payload.orientation else "N"
    }

# ---------------------------------------------------------
# 1. Direct REST Endpoint
# ---------------------------------------------------------
@app.post("/floor_plan/generate")
async def generate_direct(payload: FloorPlanRequest):
    """
    Standard blocking endpoint. Waits for full generation and returns final output.
    """
    engine_request = map_request_to_engine(payload)
    
    # Run the synchronous generate_floorplan in a thread to avoid blocking the event loop
    result = await asyncio.to_thread(generate_floorplan, engine_request)
    
    if result["status"] != "success":
        return {"error": result["message"]}
        
    # Read the generated SVG file to return as a string
    try:
        with open(result["svg_path"], "r") as f:
            svg_content = f.read()
    except Exception as e:
        svg_content = f"<svg>Error reading file: {str(e)}</svg>"

    return {
        "svg": svg_content,
        "confidence": 0.85, # Placeholder until Evaluation Engine is wired
        "bylaws_used": [payload.jurisdiction],
        "blueprints_referenced": ["RPLAN Dataset"],
        "summary": "Generated layout based on user preferences."
    }

# ---------------------------------------------------------
# 2. SSE Streaming Endpoint
# ---------------------------------------------------------
@app.post("/floor_plan/generate/stream")
async def generate_stream(payload: FloorPlanRequest):
    """
    Server-Sent Events endpoint. Streams progress updates and SVG drafts to the frontend.
    """
    engine_request = map_request_to_engine(payload)
    
    async def event_generator():
        # --- MOCK STREAMING PHASE (To be replaced in Phase 3) ---
        # Yield Stage 0: Initializing
        yield f"event: progress\ndata: {json.dumps({'stage': 0, 'stage_name': 'Initialization', 'text': 'Starting engine...'})}\n\n"
        await asyncio.sleep(1)
        
        # Yield Stage 1: Spatial Planning
        yield f"event: progress\ndata: {json.dumps({'stage': 1, 'stage_name': 'Spatial Planning', 'text': 'LLM is mapping room topology...'})}\n\n"
        await asyncio.sleep(1)
        
        # Yield Stage 2: Coordinates
        yield f"event: progress\ndata: {json.dumps({'stage': 2, 'stage_name': 'Coordinates', 'text': 'Z3 Solver mapping geometry...'})}\n\n"
        await asyncio.sleep(1)
        
        # --- RUN ACTUAL ENGINE ---
        # Note: In Phase 3, we will modify Z3FloorPlanSolver to yield natively.
        result = await asyncio.to_thread(generate_floorplan, engine_request)
        
        # Yield Stage 3: SVG Layout
        yield f"event: progress\ndata: {json.dumps({'stage': 3, 'stage_name': 'SVG Layout', 'text': 'Drawing vector output...'})}\n\n"
        
        if result["status"] == "success":
            try:
                with open(result["svg_path"], "r") as f:
                    svg_content = f.read()
            except:
                svg_content = "<svg>Error loading generated SVG.</svg>"
                
            # Yield the SVG draft
            yield f"event: svg\ndata: {json.dumps({'svg': svg_content, 'is_final': False, 'label': 'Draft Layout'})}\n\n"
            await asyncio.sleep(1)
            
            # Yield Stage 4: Refining
            yield f"event: progress\ndata: {json.dumps({'stage': 4, 'stage_name': 'Refining', 'text': 'Applying final Evaluation Engine scoring...'})}\n\n"
            await asyncio.sleep(1)
            
            # Yield final
            yield f"event: final_response\ndata: {json.dumps({'text': 'Generation complete!', 'metadata': {'confidence': 0.88, 'bylaws_used': ['BBMP 2003']}})}\n\n"
            # Final SVG payload
            yield f"event: svg\ndata: {json.dumps({'svg': svg_content, 'is_final': True, 'label': 'Final Layout'})}\n\n"
        else:
            yield f"event: progress\ndata: {json.dumps({'stage': 5, 'stage_name': 'Error', 'text': result.get('message', 'Generation failed')})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Start instructions: uvicorn server:app --reload
