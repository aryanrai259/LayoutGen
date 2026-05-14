# Dual Retrieval-Augmented Generation (Dual RAG)

Generative AI models suffer from "closed-book" reasoning, locking their knowledge to the training cutoff and lacking explicit local regulatory knowledge. LayoutGen utilizes a Dual RAG architecture to bypass this limitation.

## 1. Visual RAG (Semantic Blueprint Retrieval)
The Visual RAG biases the generative process with proven geometric precedent layouts.

- **Knowledge Base:** Curated repository of reference floor plans from the RPLAN and MSD datasets.
- **Metadata Indexing:** Unlike neural embeddings requiring massive compute, LayoutGen uses deterministic semantic metadata (e.g., "3BHK", "En-Suite", "Traditional", "North-Facing").
- **Workflow:** 
  1. User prompts for a "3-bedroom apartment with an open kitchen".
  2. Visual RAG semantically matches this to the closest precedents in the vector store.
  3. The topological data of these precedents is injected into the **Architect Agent's** context, providing structural inspiration and implicit architectural wisdom.

## 2. Legal RAG (Structured Constraint Injection)
The Legal RAG ensures that the mathematical coordinates generated comply with actual laws.

- **Knowledge Base:** Structured representations of municipal building bye-laws (e.g., BBMP 2003 guidelines).
- **Constraint Encoding:** Unstructured legal documents are preprocessed into deterministic assertions (JSON format). 
  - Example: `Setback_front >= 1.5m` or `Area(Habitable) >= 9.5m^2`.
- **Workflow:**
  1. The building code JSON objects relevant to the user's plot size and location are fetched.
  2. These constraints are injected into the **Engineer Agent's** system prompt as high-priority, immutable constraints.
  3. This hard-injection prevents the LLM from trying to "negotiate" safety standards away, ensuring rigorous adherence to local regulations.

## Advantages over Single RAG
1. **Separation of Concerns:** Design intuition (Visual) is separated from rigid legal code (Legal).
2. **Determinism:** Legal constraints are injected explicitly, bypassing the standard semantic hallucination risks associated with traditional text-retrieval RAG pipelines.
3. **Generalizability:** The Legal RAG can be swapped for different jurisdictions (e.g., switching BBMP for New York IBC) without needing to retrain the underlying visual generation engine.
