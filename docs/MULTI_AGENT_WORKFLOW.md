# The Chain: Multi-Agent Workflow

## Concept: Transactional Design State
LayoutGen prevents "context drift" typically seen in long-horizon LLMs by formalizing the design process into an immutable, transactional state ledger, called **The Chain**.

At any given step $t$, the design state $S_t$ is defined as:
$$S_t = (G_t, V_t, C_t, E_t)$$

- **$G_t$ (Graph):** Topological configuration (Bubble Diagram) of rooms and adjacencies.
- **$V_t$ (Vector):** Geometric floor plan with exact Cartesian coordinates (SVG).
- **$C_t$ (Constraints):** Active set of regulatory and cultural rules.
- **$E_t$ (Evaluation):** The multi-dimensional assessment metrics and grades.

Transitions from $S_t \rightarrow S_{t+1}$ are "gated" by an evaluation threshold. The pipeline will not progress until the layout meets minimum baseline viability, mitigating cascading failures.

---

## The Agents

### 1. Architect Agent
- **Role:** High-level spatial and topological reasoning.
- **Input:** User Prompt + Visual RAG Context (precedent layouts).
- **Task:** Generates a high-level spatial plan detailing room lists, approximate sizes, and connectivity requirements.
- **Output:** Topological Graph ($G_t$).

### 2. Engineer Agent
- **Role:** Geometric mapping and Cartesian synthesis.
- **Input:** Spatial Plan ($G_t$) + Legal RAG Constraints ($C_t$) + Previous Feedback.
- **Task:** Embeds the topological graph into a rigid coordinate system. Translates semantic relationships into precise $(x, y, w, h)$ bounding boxes while avoiding overlaps. Prompts the LLM to "show its work" mathematically.
- **Output:** Vector Plan ($V_t$) formatted as valid SVG markup.

### 3. Evaluation Agent (The Auditor)
- **Role:** Rule-based and LLM-driven constraint checking.
- **Input:** Vector Plan ($V_t$) + Legal Constraints + Vaastu rules.
- **Task:** Evaluates the geometry across Compliance, Design Quality, and Sustainability. Translates errors into actionable natural language feedback.
- **Output:** Evaluation Report ($E_t$) containing scores, grades (A+ to F), and a feedback string.

---

## The Feedback Loop (Self-Correction)
If $E_t$ yields a poor grade, the system initiates a self-correction iteration.
The errors are categorized by a taxonomy of spatial hallucinations:
1. **Type I (Topological):** Incorrect connections (e.g., Bedroom only accessible via bathroom).
2. **Type II (Geometric):** Invalid polygons (e.g., Overlapping walls).
3. **Type III (Regulatory):** Correct shape, but non-compliant (e.g., Kitchen $< 5m^2$).

The specific $\Delta E$ error is appended to the Engineer Agent's context window as an explicit instruction for Iteration $t+1$:
> *"Living room aspect ratio is 3.2:1, adjust toward Golden Ratio (1.618:1)"*

This loop runs iteratively (max 3-5 times) until saturation is reached.
