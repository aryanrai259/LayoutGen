import os
import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from main import generate_floorplan_stream

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
    Standard blocking endpoint. Consumes the stream and returns final output.
    """
    engine_request = map_request_to_engine(payload)
    
    # Consume the generator to the end
    final_svg = "<svg>Error</svg>"
    error_msg = None
    
    for event in generate_floorplan_stream(engine_request):
        if event.get("type") == "error":
            error_msg = event.get("text")
        elif event.get("type") == "svg" and event.get("is_final"):
            final_svg = event.get("svg")

    if error_msg:
        return {"error": error_msg}

    return {
        "svg": final_svg,
        "confidence": 0.85,
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
        # Iterate over the true Agentic yields from main.py
        for event_data in generate_floorplan_stream(engine_request):
            
            # Format according to our frontend requirements
            event_type = event_data.get("type", "progress")
            
            if event_type == "progress":
                yield f"event: progress\ndata: {json.dumps(event_data)}\n\n"
            
            elif event_type == "svg":
                yield f"event: svg\ndata: {json.dumps(event_data)}\n\n"
                
            elif event_type == "error":
                yield f"event: progress\ndata: {json.dumps(event_data)}\n\n"
                
            elif event_type == "final":
                yield f"event: final_response\ndata: {json.dumps(event_data)}\n\n"
            
            # We add a tiny async sleep so FastAPI flushes the network buffer to the client
            await asyncio.sleep(0.01)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Start instructions: uvicorn server:app --reload
