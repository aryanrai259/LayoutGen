# FloorplanAI - Complete Architecture & Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [How We Differ from Traditional RAG](#how-we-differ-from-traditional-rag)
4. [LLM Usage in Our System](#llm-usage-in-our-system)
5. [Complete File Structure](#complete-file-structure)
6. [System Workflow](#system-workflow)
7. [Component Details](#component-details)
8. [Use Cases](#use-cases)
9. [API Reference](#api-reference)
10. [Setup & Installation](#setup--installation)
11. [Configuration](#configuration)
12. [Data Flow](#data-flow)

---

## Project Overview

**FloorplanAI** is an AI-powered floor plan generation system that creates compliant, optimized 2D residential layouts using:

- **Dual-RAG System**: Retrieves legal regulations and layout patterns from vector databases
- **LLM Topology Planning**: Uses Groq (Llama 3) to generate room adjacencies and spatial relationships
- **Neuro-Symbolic Reasoning**: Z3 constraint solver ensures geometric validity
- **Vaastu Compliance**: Applies traditional Indian architectural principles
- **CAD-Ready Output**: Generates both DXF (CAD) and SVG (web) formats

### Key Features

✅ **Legal Compliance**: BBMP/NBC building bye-laws via RAG-Regulations  
✅ **Pattern Optimization**: 17,000+ ResPlan dataset patterns via RAG-Patterns  
✅ **Vaastu Alignment**: Static directional rules for room placement  
✅ **Geometric Validity**: Z3 constraint solver with hard and soft constraints  
✅ **Professional Output**: DXF for CAD software, SVG for web visualization  
✅ **Streamlit UI**: Interactive web interface for easy floor plan generation  

---

## How We Differ from Traditional RAG

### Traditional RAG Pipeline
```
User Query → Vector Search → Retrieve Documents → LLM Generates Text Answer
```
**Example:** "What are kitchen building codes?" → Text explanation

### Our System: Hybrid RAG + Neuro-Symbolic AI
```
User Request → Dual-RAG Retrieval → LLM Adjacency Suggestions → Z3 Geometric Solver → CAD Floor Plan
```

**Key Differences:**

| Aspect | Traditional RAG | Our System |
|--------|----------------|------------|
| **Output** | Text/Answer | **Geometric Floor Plan** (DXF/SVG) |
| **LLM Role** | Primary generator | **Advisory only** (adjacency optimization) |
| **Reasoning** | LLM reasoning | **Symbolic reasoning** (Z3 solver) |
| **Structure** | Unstructured text | **Structured geometry** (x, y, w, h) |
| **Guarantees** | None | **Hard constraints** (legal, geometric) |
| **RAG Usage** | Single RAG | **Dual-RAG** (patterns + regulations) |
| **Fallback** | LLM-only | **Deterministic fallback** (works without LLM) |

**Why This Architecture?**
- **Geometric Precision**: Z3 solver ensures rooms don't overlap, fit in plot
- **Legal Compliance**: Hard constraints from regulations must be satisfied
- **Stability**: Deterministic room generation ensures consistent output
- **Multi-Modal Knowledge**: Patterns + Regulations + Vaastu + Geometric constraints

---

## LLM Usage in Our System

### Location: `backend/planner/llm_topology.py`

**LLM Role:** **Adjacency Optimization Only** (optional enhancement)

**What LLM Does:**
- ✅ Suggests optimal room adjacencies (which rooms should connect)
- ✅ Learns from RAG patterns (applying proven layouts)
- ✅ Enhances connectivity (optional improvement)

**What LLM Does NOT Do:**
- ❌ Generate room names (deterministic generator does this)
- ❌ Create room list (deterministic generator does this)
- ❌ Geometric layout (Z3 solver does this)
- ❌ Legal constraints (RAG + JSON rules do this)

### LLM Workflow

```
1. Deterministic generator creates standard rooms: ["Living_Hall", "Kitchen", ...]
2. Deterministic generator creates base adjacencies: [["Living_Hall", "Kitchen"], ...]
3. LLM receives: room list (fixed), base adjacencies, RAG patterns, user preferences
4. LLM outputs: optimized adjacencies (suggestions only)
5. System validates: checks room IDs exist, ensures Entrance → Living_Hall
6. If LLM fails: falls back to deterministic adjacencies (system continues working)
```

### LLM Model
- **Provider:** Groq
- **Model:** Llama 3.3 70B Versatile
- **Temperature:** 0.2 (low, for consistency)
- **Format:** JSON object (forced)

### Why Limited Role?
1. **Reliability**: LLMs unreliable for structured output → deterministic generation
2. **Consistency**: Same input → same room names → deterministic structure
3. **Geometric Validity**: LLMs can't ensure constraints → Z3 solver handles this
4. **Legal Compliance**: Hard constraints from regulations → not LLM-generated
5. **Fallback**: System works without LLM → deterministic adjacencies always available

**Called From:** `backend/fusion/composer.py` → `FusionComposer.compose()` → `LLMTopologyPlanner.plan_topology()`

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                                │
│  ┌──────────────────────┐      ┌──────────────────────┐     │
│  │ Streamlit App (app.py)│      │ CLI (main.py)         │     │
│  │ Web UI                │      │ Direct API            │     │
│  └──────────┬───────────┘      └──────────┬────────────┘     │
└─────────────┼──────────────────────────────┼──────────────────┘
              │                              │
              └──────────────┬───────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MAIN ORCHESTRATOR (main.py)                  │
│  • Receives user request                                        │
│  • Coordinates pipeline execution                               │
│  • Returns generated floor plans                                │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: FUSION COMPOSER                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 1. RAG Retrieval (MasterRetriever)                       │ │
│  │    • Patterns: Query ResPlan dataset (17k layouts)        │ │
│  │    • Regulations: Query BBMP compliance documents        │ │
│  │    • Hard Rules: Load static JSON constraints            │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 2. LLM Topology Planning (LLMTopologyPlanner)             │ │
│  │    • Groq API (Llama 3.3 70B)                            │ │
│  │    • Generates room adjacencies                           │ │
│  │    • Injects corridors for multi-bedroom layouts         │ │
│  │    • Creates spatial relationships                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 3. Vaastu Integration (vaastu/mapper.py)                │ │
│  │    • Loads directional preferences                        │ │
│  │    • Maps room types to preferred zones                   │ │
│  └──────────────────────────────────────────────────────────┘ │
│  Output: Semantic Layout JSON (rooms, adjacencies, constraints) │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2: Z3 CONSTRAINT SOLVER                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ HARD CONSTRAINTS (Must Satisfy)                          │ │
│  │ • Plot boundaries (strict limits)                       │ │
│  │ • Minimum sizes (area, width, height)                    │ │
│  │ • Aspect ratio limits (w ≤ 2.5h, h ≤ 2.5w)              │ │
│  │ • No overlaps between rooms                              │ │
│  │ • Shared wall adjacencies (1m minimum overlap)           │ │
│  │ • Grid snapping (0.5m grid)                              │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ SOFT OBJECTIVES (Optimize)                                │ │
│  │ • Vaastu preferences (minimize distance to zones)        │ │
│  │ • Compactness (minimize bounding box)                   │ │
│  │ • Alignment (encourage aligned walls)                     │ │
│  │ • Interior compactness (minimize unused space)          │ │
│  └──────────────────────────────────────────────────────────┘ │
│  Output: Geometric Layout (x, y, w, h per room)               │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3: RENDERERS                            │
│  ┌──────────────────────┐      ┌──────────────────────┐       │
│  │ Architectural       │      │ DXF Renderer          │       │
│  │ Renderer (SVG)     │      │ (CAD Format)          │       │
│  │                     │      │                      │       │
│  │ • Plot boundary     │      │ • Plot boundary       │       │
│  │ • Rooms with colors │      │ • Rooms with colors   │       │
│  │ • Labels & dims    │      │ • Room labels         │       │
│  │ • Grid overlay      │      │ • CAD-compatible      │       │
│  │ • Legend & north    │      │                      │       │
│  └──────────────────────┘      └──────────────────────┘       │
│  Output: plan_XXX.svg, plan_XXX.dxf                             │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Diagram

```
User Request
    │
    ├─→ FusionComposer.compose()
    │   │
    │   ├─→ MasterRetriever.retrieve_patterns()
    │   │   └─→ Qdrant (patterns_resplan collection)
    │   │
    │   ├─→ MasterRetriever.retrieve_soft_rules()
    │   │   └─→ Qdrant (regulations_chunks collection)
    │   │
    │   ├─→ MasterRetriever.get_hard_rules()
    │   │   └─→ table_rules.json
    │   │
    │   ├─→ LLMTopologyPlanner.plan_topology()
    │   │   └─→ Groq API (Llama 3.3 70B)
    │   │
    │   └─→ get_vaastu_zones()
    │       └─→ vaastu_rules.json
    │
    ├─→ Z3FloorPlanSolver.solve()
    │   └─→ Z3 Optimize() with lexicographic priority
    │
    └─→ Renderers (SVG + DXF)
        └─→ Output files
```

---

## Complete File Structure

```
floorplanai/
├── app.py                          # Streamlit web UI
├── main.py                         # Main entry point (CLI/API)
├── README.md                       # Project overview & quick start
├── ARCHITECTURE_AND_DOCUMENTATION.md  # This file
├── requirements.txt                # Root dependencies
│
├── backend/                        # Core backend application
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   ├── requirements.txt            # Backend dependencies
│   ├── test_setup.py               # Setup verification
│   │
│   ├── planner/                    # Phase 1: LLM Topology Planning
│   │   ├── __init__.py
│   │   └── llm_topology.py         # Groq-based topology planner
│   │
│   ├── fusion/                     # Phase 1: Fusion Layer
│   │   ├── __init__.py
│   │   ├── composer.py             # Combines RAG + LLM + Vaastu
│   │   └── prompts.py              # LLM prompt templates (unused)
│   │
│   ├── rag/                        # RAG (Retrieval-Augmented Generation)
│   │   ├── __init__.py
│   │   ├── retriever.py            # MasterRetriever (unified interface)
│   │   ├── ingest.py               # Legacy ingestion (may be unused)
│   │   ├── table_rules.json        # Hard constraints (fallback rules)
│   │   │
│   │   ├── regulations/            # RAG-Regulations: Legal compliance
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py           # PDF ingestion into Qdrant
│   │   │   ├── retriever.py        # Regulation retrieval (legacy)
│   │   │   └── sources/            # Compliance PDFs
│   │   │       ├── Bangalore-Building-Byelaws (2).pdf
│   │   │       └── Master Compliance Manual_ Residential Floor Plan Design (BBMP 2003).pdf
│   │   │
│   │   └── patterns/               # RAG-Patterns: Layout patterns
│   │       ├── __init__.py
│   │       ├── ingest.py           # ResPlan dataset ingestion
│   │       ├── retriever.py        # Pattern retrieval (legacy)
│   │       ├── embedding.py        # Embedding utilities
│   │       └── datasets/            # ResPlan dataset
│   │           ├── __init__.py
│   │           ├── ResPlan.pkl     # 17,000+ floor plan layouts
│   │           ├── debug_resplan.py
│   │           └── resplan_utils.py
│   │
│   ├── vaastu/                     # Vaastu compliance
│   │   ├── __init__.py
│   │   ├── mapper.py               # Vaastu rule mapping
│   │   └── vaastu_rules.json       # Static Vaastu rules
│   │
│   ├── solver/                     # Phase 2: Z3 Constraint Solver
│   │   ├── __init__.py
│   │   ├── z3_solver.py            # Main Z3 solver
│   │   └── constraints.py          # Constraint builder utilities
│   │
│   ├── renderer/                   # Phase 3: Output Renderers
│   │   ├── __init__.py
│   │   ├── architectural_renderer.py  # SVG renderer (web)
│   │   ├── dxf_renderer.py         # DXF renderer (CAD)
│   │   └── svg_renderer.py         # Legacy SVG renderer
│   │
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   ├── pdf_utils.py            # PDF text & table extraction
│   │   ├── chunking.py             # Text chunking for RAG
│   │   └── validators.py            # Layout validation
│   │
│   └── scripts/                    # Setup & test scripts
│       ├── __init__.py
│       ├── create_collections.py   # Qdrant collection creation
│       └── render_test.py           # Rendering tests
│
├── qdrant_storage/                 # Local Qdrant vector database
│   ├── collections/
│   │   ├── patterns_resplan/       # Pattern embeddings
│   │   └── regulations_chunks/    # Regulation embeddings
│   └── raft_state.json
│
├── outputs/                        # Generated floor plans
│   ├── plan_YYYYMMDD_HHMMSS.svg
│   └── plan_YYYYMMDD_HHMMSS.dxf
│
└── test_*.py                       # Test scripts
```

---

## System Workflow

### Complete Pipeline Flow

#### **Step 1: User Input**

**Entry Points:**
- **Streamlit UI** (`app.py`): Interactive web interface
- **CLI/API** (`main.py`): Direct function call

**Input Format:**
```python
{
    "plot_length": 15.0,        # meters
    "plot_width": 12.0,        # meters
    "num_bedrooms": 3,
    "user_preferences": "modern open kitchen with island, large master bedroom",
    "vaastu_enabled": True,
    "orientation": "N"         # N/S/E/W
}
```

**Location:** `main.py` → `generate_floorplan()`

---

#### **Step 2: Fusion Composition**

**Location:** `backend/fusion/composer.py` → `FusionComposer.compose()`

**Process:**

1. **RAG Pattern Retrieval**
   - Query: `"{num_bedrooms}BHK layout {user_preferences}"`
   - Searches Qdrant `patterns_resplan` collection
   - Returns top-3 similar layouts from ResPlan dataset
   - Extracts: adjacencies, area ratios, room counts

2. **RAG Regulation Retrieval**
   - Query: Enhanced with user preferences
   - Searches Qdrant `regulations_chunks` collection
   - Returns top-5 relevant regulation chunks
   - Extracts: min areas, min widths, setbacks

3. **Hard Rules Loading**
   - Loads `table_rules.json` for fallback constraints
   - Provides baseline min_area, min_width per room type

4. **LLM Topology Planning**
   - Calls Groq API (Llama 3.3 70B)
   - Input: User request + RAG patterns + Vaastu rules
   - Generates: Room list, adjacencies, corridors
   - **Key Feature**: Injects corridors for multi-bedroom layouts

5. **Vaastu Integration**
   - Loads `vaastu_rules.json`
   - Maps room types to preferred/allowed/forbidden zones
   - Applies orientation-based constraints

**Output: Semantic Layout JSON**
```json
{
    "project_meta": {
        "plot_length": 15.0,
        "plot_width": 12.0,
        "orientation": "N"
    },
    "rooms": [
        {
            "id": "Living_Hall",
            "type": "living",
            "legal": {
                "min_area": 22.0,
                "min_width": 3.5,
                "min_height": 2.4
            },
            "vaastu": {
                "preferred_zones": ["NE", "E", "N"],
                "allowed_zones": ["NW", "SE"],
                "forbidden_zones": ["SW"]
            }
        },
        {
            "id": "Corridor_1",
            "type": "circulation",
            "min_width": 4.0
        },
        ...
    ],
    "adjacencies": [
        ["Living_Hall", "Corridor_1"],
        ["Corridor_1", "Bedroom_1"],
        ...
    ]
}
```

---

#### **Step 3: Z3 Constraint Solving**

**Location:** `backend/solver/z3_solver.py` → `Z3FloorPlanSolver.solve()`

**Process:**

1. **Create Variables**
   - For each room: `x, y, w, h` (Real variables)
   - Position: `(x, y)` = bottom-left corner
   - Dimensions: `w` = width, `h` = height

2. **Hard Constraints (Must Satisfy)**
   - **Strict Plot Boundaries**: `x + w ≤ plot_width`, `y + h ≤ plot_length`
   - **Minimum Sizes**: `w ≥ min_width`, `h ≥ min_height`, `w × h ≥ min_area`
   - **Aspect Ratio**: `w ≤ 2.5 × h` AND `h ≤ 2.5 × w`
   - **No Overlaps**: For each room pair, ensure no overlap
   - **Shared Wall Adjacencies**: Rooms must share walls with ≥1m overlap
   - **Grid Snapping**: Positions and dimensions snap to 0.5m grid

3. **Soft Objectives (Optimize)**
   - **Vaastu Preference**: Minimize distance from room center to preferred zones
   - **Compactness**: Minimize bounding box of all rooms
   - **Alignment**: Encourage aligned walls (left/right/bottom/top edges)
   - **Interior Compactness**: Minimize unused interior space

4. **Solve**
   - Z3 `Optimize()` with lexicographic priority
   - Timeout: 50 seconds
   - Accepts `sat` (satisfiable) OR `unknown` (feasible solution)

**Output: Geometric Layout**
```json
{
    "status": "success",
    "solution": {
        "Living_Hall": {"x": 2.0, "y": 8.0, "w": 5.0, "h": 4.0},
        "Kitchen": {"x": 7.0, "y": 8.0, "w": 3.0, "h": 3.0},
        "Corridor_1": {"x": 2.0, "y": 4.0, "w": 8.0, "h": 1.0},
        "Bedroom_1": {"x": 2.0, "y": 0.0, "w": 4.0, "h": 4.0},
        ...
    }
}
```

---

#### **Step 4: Rendering**

**Location:** `backend/renderer/`

**SVG Renderer** (`architectural_renderer.py`):
- Draws plot boundary
- Draws rooms with semi-transparent colors
- Adds room labels and dimensions
- Adds grid overlay (optional)
- Adds legend and north arrow

**DXF Renderer** (`dxf_renderer.py`):
- Draws plot boundary (blue, thick line)
- Draws rooms with colors per room type
- Adds room labels
- Exports CAD-compatible DXF format

**Output Files:**
- `outputs/plan_YYYYMMDD_HHMMSS.svg` (web visualization)
- `outputs/plan_YYYYMMDD_HHMMSS.dxf` (CAD file)

---

## Component Details

### 1. Main Entry Point (`main.py`)

**Purpose:** Orchestrates the complete pipeline

**Key Function:**
```python
def generate_floorplan(user_request, output_dir="outputs")
```

**Process:**
1. Creates output directory
2. Calls `FusionComposer.compose()` → Semantic layout
3. Calls `Z3FloorPlanSolver.solve()` → Geometric layout
4. Calls renderers → SVG + DXF files
5. Returns result with file paths

**Returns:**
```python
{
    "status": "success",
    "svg_path": "outputs/plan_XXX.svg",
    "dxf_path": "outputs/plan_XXX.dxf",
    "stats": {
        "rooms": 5,
        "area": 180.0
    }
}
```

---

### 2. Streamlit UI (`app.py`)

**Purpose:** Interactive web interface

**Features:**
- Input form: Plot dimensions, bedrooms, preferences
- Generate button: Triggers floor plan generation
- SVG preview: Displays generated floor plan
- Download buttons: SVG and DXF files

**Usage:**
```bash
streamlit run app.py
```

---

### 3. Fusion Composer (`backend/fusion/composer.py`)

**Purpose:** Combines all knowledge sources into semantic layout

**Key Class:** `FusionComposer`

**Components:**
- `MasterRetriever`: RAG retrieval (patterns + regulations + hard rules)
- `LLMTopologyPlanner`: Groq-based topology generation
- `get_vaastu_zones()`: Vaastu rule application

**Key Method:**
```python
def compose(self, user_request: Dict[str, Any]) -> Dict[str, Any]
```

**Process:**
1. Retrieves patterns from ResPlan dataset
2. Retrieves regulations from BBMP documents
3. Loads hard rules from JSON
4. Calls LLM to generate topology
5. Enriches rooms with legal and Vaastu constraints
6. Returns semantic layout JSON

---

### 4. LLM Topology Planner (`backend/planner/llm_topology.py`)

**Purpose:** Generates room adjacencies and spatial relationships using LLM

**Key Class:** `LLMTopologyPlanner`

**LLM:** Groq API (Llama 3.3 70B Versatile)

**Key Features:**
- **Corridor Injection**: Automatically adds corridors for multi-bedroom layouts
- **Hub-and-Spoke**: Living room as central hub
- **Privacy**: Bedrooms connect to corridor, not directly to living room

**Key Method:**
```python
def plan_topology(
    self,
    user_request: Dict[str, Any],
    rag_patterns: List[Dict[str, Any]],
    vaastu_rules: Dict[str, Any]
) -> Dict[str, Any]
```

**Output Format:**
```json
{
    "rooms": [
        {"id": "Living_Hall", "type": "living", "min_area": 150},
        {"id": "Corridor_1", "type": "circulation", "min_width": 4}
    ],
    "adjacencies": [
        ["Living_Hall", "Corridor_1"],
        ["Corridor_1", "Bedroom_1"]
    ],
    "relative_constraints": [],
    "reasoning": "Explanation"
}
```

**Fallback:** If Groq API fails, uses deterministic fallback topology

---

### 5. Master Retriever (`backend/rag/retriever.py`)

**Purpose:** Unified interface for RAG retrieval

**Key Class:** `MasterRetriever`

**Components:**
- Qdrant client connection
- SentenceTransformer model (`all-MiniLM-L6-v2`)
- Hard rules loader (`table_rules.json`)

**Key Methods:**

1. **`retrieve_patterns(query, limit=3)`**
   - Searches `patterns_resplan` collection
   - Returns similar layouts from ResPlan dataset

2. **`retrieve_soft_rules(query, limit=5)`**
   - Searches `regulations_chunks` collection
   - Returns relevant regulation chunks

3. **`get_hard_rules(room_type)`**
   - Returns static constraints from `table_rules.json`
   - Provides fallback min_area, min_width per room type

---

### 6. Z3 Solver (`backend/solver/z3_solver.py`)

**Purpose:** Generates geometric layout from semantic layout

**Key Class:** `Z3FloorPlanSolver`

**Key Features:**
- **Strict Plot Limits**: Prevents rooms from exceeding plot boundaries
- **Shared Wall Adjacencies**: Forces 1m minimum overlap for doors
- **Grid Snapping**: 0.5m grid for clean values
- **Lexicographic Optimization**: Prevents objective thrashing

**Key Method:**
```python
def solve(self) -> Dict[str, Any]
```

**Hard Constraints:**
- Plot boundaries
- Minimum sizes
- Aspect ratios
- No overlaps
- Shared wall adjacencies
- Grid snapping

**Soft Objectives:**
- Vaastu preferences
- Compactness
- Alignment
- Interior compactness

**Solver Configuration:**
- Lexicographic priority
- 50-second timeout
- Accepts `sat` OR `unknown`

---

### 7. Renderers

#### SVG Renderer (`backend/renderer/architectural_renderer.py`)

**Purpose:** Web-ready visualization

**Features:**
- Plot boundary
- Rooms with semi-transparent colors
- Room labels and dimensions
- Grid overlay (optional)
- Legend and north arrow

#### DXF Renderer (`backend/renderer/dxf_renderer.py`)

**Purpose:** CAD-compatible output

**Features:**
- Plot boundary (blue, thick line)
- Rooms with colors per room type
- Room labels
- CAD-compatible format

---

### 8. Vaastu Mapper (`backend/vaastu/mapper.py`)

**Purpose:** Applies Vaastu directional rules

**Key Function:**
```python
def get_vaastu_zones(room_type: str) -> Dict[str, List[str]]
```

**Returns:**
```python
{
    "preferred": ["NE", "E", "N"],
    "allowed": ["NW", "SE"],
    "avoid": ["SW"]
}
```

**Data Source:** `vaastu_rules.json`

---

## Use Cases

### Use Case 1: Generate 3BHK Floor Plan

**Input:**
```python
{
    "plot_length": 15.0,
    "plot_width": 12.0,
    "num_bedrooms": 3,
    "user_preferences": "modern open kitchen, large master bedroom",
    "vaastu_enabled": True,
    "orientation": "N"
}
```

**Process:**
1. RAG retrieves 3BHK patterns and regulations
2. LLM generates topology with corridor
3. Z3 solver creates geometric layout
4. Renderers generate SVG and DXF

**Output:** Compliant 3BHK floor plan with corridor connecting bedrooms

---

### Use Case 2: Custom Layout with Preferences

**Input:**
```python
{
    "plot_length": 18.0,
    "plot_width": 12.0,
    "num_bedrooms": 2,
    "user_preferences": "open kitchen with island, spacious living area, balcony",
    "vaastu_enabled": True,
    "orientation": "E"
}
```

**Process:**
- User preferences enhance RAG queries
- LLM considers preferences in topology
- Z3 solver optimizes for preferences
- Output matches user style

---

### Use Case 3: Minimal Input (Defaults)

**Input:**
```python
{
    "plot_length": 12.0,
    "plot_width": 10.0,
    "num_bedrooms": 1,
    "user_preferences": "",
    "vaastu_enabled": False,
    "orientation": "N"
}
```

**Process:**
- System uses default RAG queries
- Fallback topology if LLM unavailable
- Basic constraints applied
- Simple 1BHK layout generated

---

## API Reference

### Main Function

**Function:** `generate_floorplan(user_request, output_dir="outputs")`

**Parameters:**
- `user_request` (dict): User input with plot dimensions, bedrooms, preferences
- `output_dir` (str): Output directory for generated files

**Returns:**
```python
{
    "status": "success" | "error",
    "svg_path": "outputs/plan_XXX.svg",
    "dxf_path": "outputs/plan_XXX.dxf",
    "stats": {
        "rooms": int,
        "area": float
    },
    "message": str  # Only if error
}
```

---

## Setup & Installation

### Prerequisites

- Python 3.8+
- Qdrant running locally (http://localhost:6333) or remote instance
- ResPlan dataset (`ResPlan.pkl`) in `backend/rag/patterns/datasets/`
- Groq API key (optional, for LLM topology planning)

### Installation Steps

1. **Clone Repository**
```bash
git clone <repository-url>
cd floorplanai
```

2. **Install Dependencies**
```bash
# Root dependencies
pip install -r requirements.txt

# Backend dependencies
pip install -r backend/requirements.txt
```

3. **Set Up Environment Variables**
Create `.env` file:
```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Optional, for remote Qdrant

# Embedding Model
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# LLM Configuration (Optional)
GROQ_API_KEY=your_groq_api_key_here

# Collection Names
REGULATIONS_COLLECTION_NAME=regulations_chunks
PATTERNS_COLLECTION_NAME=patterns_resplan
```

4. **Start Qdrant (if running locally)**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

5. **Ingest Data**

**Regulations:**
```bash
cd backend
python -m rag.regulations.ingest
```

**Patterns:**
```bash
python -m rag.patterns.ingest
```

6. **Run Application**

**Streamlit UI:**
```bash
streamlit run app.py
```

**CLI:**
```bash
python main.py
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_URL` | Qdrant server URL | `http://localhost:6333` |
| `QDRANT_API_KEY` | Qdrant API key (optional) | `None` |
| `EMBEDDING_MODEL_NAME` | SentenceTransformer model | `all-MiniLM-L6-v2` |
| `GROQ_API_KEY` | Groq API key for LLM | `None` |
| `REGULATIONS_COLLECTION_NAME` | Regulations collection | `regulations_chunks` |
| `PATTERNS_COLLECTION_NAME` | Patterns collection | `patterns_resplan` |

### Configuration File (`backend/config.py`)

Contains centralized configuration:
- Qdrant settings
- Embedding model settings
- Collection names
- Paths to data files

---

## Data Flow

### Complete Data Flow Diagram

```
User Request (JSON)
    │
    ├─→ main.py::generate_floorplan()
    │   │
    │   ├─→ FusionComposer.compose()
    │   │   │
    │   │   ├─→ MasterRetriever.retrieve_patterns()
    │   │   │   ├─→ SentenceTransformer.encode()
    │   │   │   └─→ Qdrant.search(patterns_resplan)
    │   │   │
    │   │   ├─→ MasterRetriever.retrieve_soft_rules()
    │   │   │   ├─→ SentenceTransformer.encode()
    │   │   │   └─→ Qdrant.search(regulations_chunks)
    │   │   │
    │   │   ├─→ MasterRetriever.get_hard_rules()
    │   │   │   └─→ table_rules.json
    │   │   │
    │   │   ├─→ LLMTopologyPlanner.plan_topology()
    │   │   │   └─→ Groq API (Llama 3.3 70B)
    │   │   │
    │   │   └─→ get_vaastu_zones()
    │   │       └─→ vaastu_rules.json
    │   │
    │   ├─→ Z3FloorPlanSolver.solve()
    │   │   ├─→ Create Z3 variables (x, y, w, h)
    │   │   ├─→ Add hard constraints
    │   │   ├─→ Add soft objectives
    │   │   └─→ Z3 Optimize()
    │   │
    │   └─→ Renderers
    │       ├─→ ArchitecturalRenderer.render() → SVG
    │       └─→ DXFRenderer.render() → DXF
    │
    └─→ Output Files (SVG + DXF)
```

### Data Formats

**Input Format:**
```python
{
    "plot_length": float,      # meters
    "plot_width": float,       # meters
    "num_bedrooms": int,       # >= 1
    "user_preferences": str,   # Natural language
    "vaastu_enabled": bool,
    "orientation": str         # "N" | "S" | "E" | "W"
}
```

**Semantic Layout Format:**
```json
{
    "project_meta": {
        "plot_length": float,
        "plot_width": float,
        "orientation": str
    },
    "rooms": [
        {
            "id": str,
            "type": str,
            "legal": {
                "min_area": float,
                "min_width": float,
                "min_height": float
            },
            "vaastu": {
                "preferred_zones": [str],
                "allowed_zones": [str],
                "forbidden_zones": [str]
            }
        }
    ],
    "adjacencies": [[str, str]]
}
```

**Geometric Layout Format:**
```json
{
    "status": "success",
    "solution": {
        "room_id": {
            "x": float,
            "y": float,
            "w": float,
            "h": float
        }
    }
}
```

---

## Key Design Decisions

### 1. Dual-RAG System
- **Separate Collections**: Regulations and patterns in different Qdrant collections
- **Different Strategies**: Top-5 regulations, top-3 patterns
- **Independent Optimization**: Can tune each RAG system separately

### 2. LLM Topology Planning
- **Groq API**: Fast, quota-free inference with Llama 3.3 70B
- **Corridor Injection**: Automatically adds circulation for multi-bedroom layouts
- **Fallback**: Deterministic topology if LLM unavailable

### 3. Z3 Constraint Hierarchy
- **Hard Constraints**: Must satisfy (boundaries, sizes, adjacencies)
- **Soft Objectives**: Optimize (Vaastu, compactness, alignment)
- **Lexicographic Priority**: Prevents objective thrashing

### 4. Grid Snapping
- **0.5m Grid**: Produces clean values (4.0, 3.5 instead of 4.01875)
- **CAD Compatibility**: Better for professional CAD software
- **Optional**: Can be disabled for flexibility

### 5. Hub-and-Spoke Layout
- **Living Room Hub**: Central hub connecting all rooms
- **Corridor System**: Bedrooms connect via corridor, not directly to living room
- **Privacy**: Ensures bedroom privacy

---

## Performance Characteristics

- **RAG Retrieval**: ~50-100ms per query (local embeddings)
- **LLM Topology**: ~1-2 seconds (Groq API)
- **Fusion Layer**: ~10-20ms (rule-based, fast)
- **Z3 Solver**: ~1-50 seconds (depends on complexity)
- **Rendering**: ~50-100ms per format
- **Total Pipeline**: ~3-60 seconds end-to-end

---

## Future Enhancements

### Phase 6: Doors and Corridors
- Add door placement logic
- Generate corridors to connect rooms
- Update renderers to show doors and corridors

### Phase 7: Wall Thickness Visualization
- Add wall thickness to room boundaries
- Update renderers to show actual wall boundaries

### Phase 8: Room Centroids and Arrows
- Visualize room centroids
- Add adjacency arrows between rooms

### Phase 9: Scale Bar
- Add scale bar to SVG output
- Improve measurement visualization

### Phase 10: Advanced Features
- Multi-story support
- Staircase placement
- Window and door placement
- Material specifications

---

## Troubleshooting

### Common Issues

1. **Qdrant Connection Error**
   - Check if Qdrant is running: `docker ps`
   - Verify `QDRANT_URL` in `.env`

2. **LLM Topology Fails**
   - Check `GROQ_API_KEY` in `.env`
   - System falls back to deterministic topology

3. **Z3 Solver Timeout**
   - Plot may be too small for requested rooms
   - Try reducing number of bedrooms
   - Check minimum size constraints

4. **No Patterns Found**
   - Verify ResPlan dataset is ingested
   - Check `patterns_resplan` collection exists

5. **No Regulations Found**
   - Verify regulations are ingested
   - Check `regulations_chunks` collection exists

---

## License

[Add your license here]

---

**Last Updated:** Based on current codebase analysis  
**Version:** 1.0  
**Status:** Core functionality complete ✅

