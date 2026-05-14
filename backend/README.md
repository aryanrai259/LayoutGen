# Compliance-Aware Agentic AI Floor Plan Designer

A Python backend system that generates 2D residential floor plans that are:
- **Legally compliant** (BBMP/NBC bye-laws via RAG-Regulations)
- **Functionally optimized** (layout adjacency patterns via RAG-Patterns)
- **Vaastu-aligned** (static directional rules)
- **Geometrically valid** (Z3 constraint solver)
- **CAD-ready** (DXF + SVG output using ezdxf)

## Architecture

```
User Input
→ LLM Reasoner (LangChain / prompt-based)
→ Dual Retrieval:
   1) RAG-Regulations (BBMP bye-laws, tables flattened into text)
   2) RAG-Patterns (ResPlan adjacency & area summaries)
→ Vaastu Rules (static JSON, NOT RAG)
→ Fusion Layer (Semantic Layout JSON)
→ Z3 Solver (hard + soft constraints)
→ DXF / SVG Renderer
```

## Project Structure

```
floorplan-ai/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── rag/
│   │   ├── regulations/        # RAG-Regulations module
│   │   └── patterns/           # RAG-Patterns module
│   │
│   ├── vaastu/                 # Vaastu rules (static JSON)
│   ├── fusion/                 # Fusion layer
│   ├── solver/                 # Z3 constraint solver
│   ├── renderer/               # DXF/SVG renderers
│   └── utils/                  # Utility functions
│
├── README.md
└── .env                        # Environment variables
```

## Setup

### Prerequisites

- Python 3.8+
- Qdrant running locally (http://localhost:6333) or remote instance
- ResPlan dataset (ResPlan.pkl) - place in `datasets/` directory

### Installation

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set up environment variables (create `.env` file):
```env
QDRANT_URL=http://localhost:6333
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
RESPLAN_DATASET_PATH=../datasets/ResPlan.pkl
```

3. Start Qdrant (if running locally):
```bash
docker run -p 6333:6333 qdrant/qdrant
```

4. Ingest regulations (place PDFs in `backend/rag/regulations/sources/`):
```bash
python -m rag.regulations.ingest
```

5. Ingest ResPlan patterns:
```bash
python -m rag.patterns.ingest
```

6. Start FastAPI server:
```bash
python main.py
# or
uvicorn main:app --reload
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Generate Floor Plan
```bash
POST /generate
Content-Type: application/json

{
  "total_area": 1200,
  "num_bedrooms": 2,
  "num_bathrooms": 2,
  "has_kitchen": true,
  "has_living": true,
  "has_dining": false,
  "plot_length": 40,
  "plot_width": 30,
  "orientation": "N",
  "vaastu_enabled": true
}
```

## Dataset Requirements

### Primary Dataset: ResPlan
- Format: Pickle file (`.pkl`)
- Expected structure:
  ```python
  {
    'plan_id': '1012',
    'rooms': [
      {'id': 0, 'type': 'living', 'bbox': [x1, y1, x2, y2]},
      ...
    ],
    'adjacencies': [(0, 1), (1, 2), ...],
    'total_area': 900.0
  }
  ```

### Regulations Sources
- Place PDF files in `backend/rag/regulations/sources/`
- System will extract tables and text automatically

## Key Features

- **Dual-RAG System**: Separate retrieval for regulations and patterns
- **Qdrant Vector Store**: Fast similarity search for both RAG systems
- **Z3 Constraint Solving**: Guarantees geometric validity
- **Vaastu Compliance**: Static rule-based directional constraints
- **CAD Export**: DXF format for professional use
- **Web Visualization**: SVG format for web display

## Development Notes

- Clean, minimal codebase optimized for debugging
- Deterministic logic preferred over LLM where possible
- No 3D, no CV models, no fine-tuning
- Scope: 2D residential layouts only

## License

[Add your license here]

