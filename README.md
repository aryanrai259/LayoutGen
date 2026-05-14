# LayoutGen (Floorplan-ai) 🏗️

Welcome to **LayoutGen**, a half-built but highly ambitious AI-powered floor plan designer. This system is designed to generate geometrically valid, legally compliant, and Vaastu-aligned 2D residential floor plans. 

This document serves as the master guide to understanding the state of the repository, how the moving pieces fit together, and what needs to be fixed to get it fully operational.

---

## 1. What This Is

LayoutGen is an AI pipeline and web application that converts a text-based prompt and basic parameters (plot size, room counts) into professional architectural floor plans (SVG for web, DXF for CAD).

The repository contains two main parts:
- **`backend/`**: A Python system utilizing a Neuro-Symbolic approach. It combines Retrieval-Augmented Generation (RAG), Large Language Models (LLMs) for spatial reasoning, and the Z3 SMT solver for geometric constraint solving.
- **`frontend/`**: A React-based web interface featuring a sleek "CAD-style" dark mode, real-time streaming updates (SSE), and an animated "Ghost Canvas" that visualizes the floor plan being drawn in real-time.

---

## 2. Why This Architecture?

Traditional RAG and LLM systems are great at returning *text*, but they fail miserably at generating strict *geometric structures* with hard physical constraints (like "rooms cannot overlap" and "must fit inside a 30x40 plot").

Our solution:
1. **RAG & LLM (The Brain)**: We use RAG to look up building bye-laws (BBMP) and reference layouts (ResPlan dataset). An LLM (Llama 3 via Groq) suggests room adjacencies and logical topology.
2. **Z3 Constraint Solver (The Math)**: The symbolic logic engine takes the LLM's topology and applies hard math. It forces rooms to snap to a grid, share walls, avoid overlaps, and optimize for Vaastu directions. 
3. **Deterministic Renderers (The Visuals)**: The math coordinates are then deterministically drawn into SVG and DXF formats.

---

## 3. How It Works (The Happy Path)

1. **User Input:** The user fills out the form on the React frontend.
2. **Request:** The UI sends a POST request to `/floor_plan/generate/stream`.
3. **Fusion Phase:** The backend queries Qdrant for legal regulations and architectural patterns, then asks the LLM to design a topological graph of the rooms.
4. **Solve Phase:** The Z3 engine calculates the exact `(x, y, width, height)` of every room.
5. **Stream Phase:** The backend streams progress events and partial SVG drafts via Server-Sent Events (SSE) back to the frontend.
6. **Visualization:** The React app's `GhostCanvas` animates the drawing of the walls based on the SSE stream. Finally, the true SVG and DXF files are provided to the user.

---

## 4. What Is Broken? (The Current State)

This is a **half-built product** with a massive missing link. While both the complex backend math and the complex frontend UI are written, they are completely disconnected.

### The Missing API Layer
The frontend is configured to send requests to `http://localhost:8000/floor_plan/generate` and `/floor_plan/generate/stream`. However, **there is no FastAPI server in the backend**. 
The `backend/main.py` is currently just a Python script with a `generate_floorplan()` function. It does not spin up a web server.

### The Missing SSE Implementation
The frontend contains intricate logic to parse an SSE stream to animate the floor plan generation (`src/utils/sseTextProcessor.js`). The backend currently has zero capability to yield these streaming updates. The engine runs synchronously in one big block.

### Legacy Clutter
- The backend still has a Streamlit UI (`backend/app.py`) which acts as a band-aid interface instead of the real React frontend.
- The frontend has multiple unused legacy components (`ResultView.jsx`, `Loader.jsx`).

---

## 5. What Needs To Be Fixed

To make this product fully functional, you must bridge the gap between the frontend and backend.

1. **Implement the FastAPI Server:** 
   Write a `server.py` or modify `main.py` in the backend using FastAPI. 
2. **Implement the REST Endpoints:**
   Create the `/floor_plan/generate` (returns final JSON) and `/floor_plan/generate/stream` (returns `StreamingResponse`) endpoints.
3. **Refactor the Solver to Yield Progress:**
   Modify `backend/main.py` and the Z3 solver so that it `yields` intermediate steps (e.g., `{"stage": 3, "svg": "<svg>..."}`) instead of just blocking until the end.
4. **Environment Configuration:**
   Provide a concrete way to set up the Qdrant database, ingest the `.pkl` datasets, and manage Groq API keys via `.env`.
5. **Cleanup:**
   Delete `backend/app.py` (Streamlit) and remove dead frontend code.

---

## 6. How To Fix It (Action Plan)

**Step 1: Write `backend/api.py`**
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
# ... import your engine ...

app = FastAPI()

@app.post("/floor_plan/generate/stream")
async def generate_stream(request: dict):
    # This needs to call an async generator version of your engine
    return StreamingResponse(engine_generator(request), media_type="text/event-stream")
```

**Step 2: Update the Engine to Yield**
Modify `Z3FloorPlanSolver` and `generate_floorplan` to be generators:
```python
yield "event: progress\ndata: {\"stage\": 1, \"text\": \"Topology planned\"}\n\n"
# run solver...
yield "event: svg\ndata: {\"svg\": \"<svg>...</svg>\"}\n\n"
```

**Step 3: Setup Scripts**
Create a `docker-compose.yml` to spin up Qdrant easily, and a `start.bat`/`start.sh` that runs both the FastAPI server (`uvicorn`) and the Vite React server (`npm run dev`) simultaneously.

---

## 7. Current Repository Structure

For deep dives into how specific systems work, read the detailed documentation files in the `docs/` folder:

```text
LayoutGen/
├── backend/                       # The Python Engine
│   ├── main.py                    # The core generation function (currently CLI-only)
│   ├── fusion/                    # RAG + LLM composition logic
│   ├── solver/                    # Z3 symbolic math constraints
│   └── renderer/                  # SVG and DXF generation
│
├── frontend/                      # The React Web App
│   ├── src/                       # UI components and hooks
│   ├── package.json               # Node dependencies
│   └── vite.config.js             # Dev server config (proxy to port 8000)
│
├── docs/                          # Detailed Architecture Specs
│   ├── backend_architecture.md    # How the LLM + Z3 math works
│   └── frontend_architecture.md   # How the UI and SSE streams work
│
└── README.md                      # This file
```
