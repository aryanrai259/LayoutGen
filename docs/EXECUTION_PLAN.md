# LayoutGen Execution & Implementation Plan

## Overview
This document outlines the phased organizational execution plan to transform the current prototype into the fully realized **LayoutGen** architecture as described in the manuscript. The goal is to build a Dual-RAG, Multi-Agent Self-Correcting floor plan synthesis framework.

---

## Phase 1: Foundational API & Orchestration Scaffold
**Goal:** Establish the missing link between the frontend and backend, and create the scaffolding for the multi-agent workflow.

1. **FastAPI Implementation**
   - Create `backend/server.py`.
   - Implement `/floor_plan/generate` (REST) and `/floor_plan/generate/stream` (SSE) endpoints.
   - Set up CORS and ensure Vite proxy connects successfully.

2. **The Chain Protocol Scaffold**
   - Implement the `DesignState` class representing $S_t = (G_t, V_t, C_t, E_t)$ (Graph, Vector, Constraints, Evaluation).
   - Create the loop manager that restricts state transitions unless an evaluation threshold (e.g., 65% / B-) is met.

3. **Agent Role Stubs**
   - **Architect Agent:** Class stub for processing textual inputs into bubble diagrams.
   - **Engineer Agent:** Class stub for converting bubble diagrams to Cartesian SVG coordinates.
   - **Evaluation Agent:** Class stub for generating the evaluation report ($E_t$).

---

## Phase 2: Dual RAG & Knowledge Integration
**Goal:** Implement the "Open-Book" retrieval systems that provide precedents and legal constraints to the LLM.

1. **Visual RAG (Semantic Blueprint Retrieval)**
   - Process the RPLAN / MSD dataset metadata.
   - Build a Qdrant collection indexed by layout typologies (e.g., "3BHK", "open-kitchen").
   - Create the retrieval function to fetch top-K precedent layouts based on user prompts.

2. **Legal RAG (Structured Constraint Injection)**
   - Encode the Bengaluru municipal building bye-laws (BBMP 2003) into a deterministic JSON knowledge base.
   - Write the context-injection logic to embed these hard constraints into the Engineer Agent's system prompt (e.g., minimum areas, widths).

---

## Phase 3: Multi-Dimensional Evaluation Engine
**Goal:** Implement the deterministic and semantic scoring functions that govern the agentic feedback loop.

1. **Compliance Scoring (40%)**
   - Code the area and width validators (e.g., Habitable room $\ge 9.5m^2$).
   - Implement the penalty logic (-1 minor, -3 moderate, -5 major, -15 critical).

2. **Design Quality Scoring (35%)**
   - Implement Circulation calculation (target 10-20% area).
   - Implement Beauty calculation (Golden Ratio $1.618$ aspect ratios).
   - Implement Balance calculation (geometric center vs weighted centroid).
   - Implement Flow calculation (distances between related rooms like Kitchen-Dining $<3m$).

3. **Sustainability Scoring (25%) & Vaastu**
   - Implement Window-to-Floor Ratio (WFR) and material efficiency metrics.
   - Implement Vaastu Shastra directional checks (SE Kitchen, SW Master, NE Living).

---

## Phase 4: Multi-Agent Refinement & Feedback Loop
**Goal:** Close the loop, allowing the Evaluation Engine to correct the Engineer Agent's hallucinations.

1. **Semantic Feedback Translation**
   - Translate numerical deltas ($\Delta E$) into natural language instructions (e.g., *"Kitchen area is 4.2sqm, increase to at least 5.0sqm"*).
2. **Iterative Pipeline Execution**
   - Wire the loop to run 3-5 iterations automatically.
   - Track score convergence (Iter 0 to Iter 3 saturation).
3. **SSE Yielding**
   - Ensure every agent step and SVG geometry update `yields` properly formatted SSE text for the React GhostCanvas.

---

## Phase 5: Testing, Validation & UI Polish
**Goal:** Ensure the system mirrors the statistical reductions in violations identified in the research.

1. **Headless Benchmarking**
   - Run $n=100$ headless generation tasks.
   - Validate that the multi-agent loop achieves an 84% reduction in regulatory violations compared to single-shot.
2. **Frontend UI Sync**
   - Verify the React GhostCanvas parses the new backend SSE payloads correctly.
   - Ensure the Final Grade (A+ to F) and sub-scores (Compliance, Design, Sustainability) render properly in the SummaryPanel.
