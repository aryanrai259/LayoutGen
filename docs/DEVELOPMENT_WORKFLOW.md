# Development Workflow & Execution Roadmap

This document serves as the **master blueprint** for all development work on LayoutGen. It defines the strict Git version control practices that must be followed and outlines the exact execution phases needed to bring the project from its current state to a fully functional release.

---

## Part 1: Advanced Git Workflow Rules

To ensure a clean, maintainable, and stable codebase, all development must adhere to the following advanced Git practices. 

### 1. Branching Strategy
We follow a strict `main` / `dev` / `feature` branch structure:

- **`main` (Production):** 
  - This branch is **sacred**. It must ALWAYS be in a working, stable, and deployable state.
  - Direct commits to `main` are strictly forbidden. 
  - Only `dev` can be merged into `main` after rigorous testing.

- **`dev` (Staging/Integration):** 
  - The active integration branch. All completed features and fixes are merged here first.
  - Acts as the staging ground to ensure different features work together cleanly before moving to `main`.

- **`feature/<name>` (New Work):** 
  - Created off the `dev` branch.
  - Used for building out new functionality (e.g., `feature/fastapi-setup`, `feature/z3-solver-integration`).

- **`fix/<name>` (Bug Fixes):** 
  - Created off the `dev` branch (or `main` if it's a hotfix).
  - Used strictly for patching bugs (e.g., `fix/sse-stream-parsing`).

### 2. Commit Guidelines
Commits must be regular, atomic (one logical change per commit), and use the **Conventional Commits** format:
- `feat: added FastAPI SSE endpoint`
- `fix: resolved Qdrant connection timeout`
- `docs: updated evaluation engine formulas`
- `refactor: cleaned up legacy Streamlit UI`

### 3. Pull Request (PR) & Merge Rules
1. **Never merge your own code directly.**
2. Complete your work on a `feature/` or `fix/` branch.
3. Open a Pull Request against the `dev` branch.
4. Ensure the PR description clearly states what was changed and why.
5. After `dev` is tested and verified as stable, open a Release PR from `dev` to `main`.

---

## Part 2: Current State (What is Built vs. What is Left)

### ✅ What is Built (The Prototype)
- **Frontend UI:** The React interface, including the intricate `GhostCanvas` animation system and dark mode CAD aesthetic.
- **Backend Algorithms:** The foundational Python logic for the Z3 symbolic constraint solver and the LLM generation topology.
- **Renderers:** The deterministic SVG and DXF conversion scripts.
- **Theoretical Scaffolding:** Comprehensive documentation on how the Multi-Agent system, Dual-RAG, and Evaluation Engine should theoretically function.

### ❌ What is Left (The Missing Links)
- **API Server:** There is no web server running on the backend. The frontend is waiting for endpoints (`/floor_plan/generate`) that do not exist.
- **SSE Streaming:** The Z3 engine runs as a single block and does not `yield` intermediate streaming updates (Server-Sent Events) to the frontend.
- **The Chain Protocol:** The actual Python implementation of the $S_t = (G_t, V_t, C_t, E_t)$ state-manager is missing.
- **Evaluation Engine Code:** The scoring formulas for Compliance, Design, and Sustainability are documented but not yet written in code.

---

## Part 3: Phased Execution Plan

All future `feature/` branches should map directly to these phases.

### Phase 1: API & Server Scaffold (`feature/api-server`)
- Initialize `FastAPI` and `Uvicorn` in `backend/server.py`.
- Create the standard JSON REST endpoint and the `StreamingResponse` SSE endpoint.
- Connect the frontend Vite proxy to the backend and ensure basic ping/pong communication works.

### Phase 2: Dual RAG Integration (`feature/dual-rag`)
- Set up the local Qdrant vector database via Docker.
- Ingest the RPLAN metadata for the **Visual RAG**.
- Encode the BBMP 2003 laws into JSON for the **Legal RAG**.
- Create the retriever scripts to fetch this context during an API call.

### Phase 3: The Chain & Agent Logic (`feature/agent-orchestration`)
- Write the `DesignState` class to manage the loop.
- Implement the **Architect Agent** (LLM call to Groq to generate bubble diagram).
- Implement the **Engineer Agent** (Z3 solver processing the bubble diagram into exact coordinates).
- Refactor the solver to `yield` progress dictionary steps for the SSE stream.

### Phase 4: Evaluation Engine (`feature/evaluation-engine`)
- Write the scoring algorithms:
  - `calculate_compliance()`: checks $9.5m^2$ minimums.
  - `calculate_design()`: checks Golden Ratio and flow distances.
  - `calculate_sustainability()`: checks WFR.
- Wire the Evaluation Agent to grade the output, and translate $\Delta E$ errors into the text feedback loop.

### Phase 5: Cleanup & Release (`dev` $\rightarrow$ `main`)
- Remove the legacy `backend/app.py` Streamlit UI.
- Verify the frontend `GhostCanvas` correctly parses the Phase 3/4 SSE streams.
- Merge `dev` into `main` for a stable v1.0.0 release.
