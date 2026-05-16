# RAG Module

Status: `planned` (logic currently implemented in `services/retriever.py`, `services/rag_orchestrator.py`, `services/llm_groq.py`)

## Responsibility
- Retrieve relevant chunks from vector store.
- Apply filters (`domain`, `lang`, `top_k`) and retrieval thresholds.
- Build grounded context with source tags (`[S1]`, `[S2]`, ...).
- Generate final answer via remote LLM API.
- Enforce guardrails (fallback, citation checks, anti-hallucination rules).

## Expected Files (target structure)
- `retrieval.py`: vector/hybrid retrieval
- `orchestrator.py`: end-to-end query flow
- `generation.py`: LLM prompting + API call
- `guardrails.py`: post-generation safety checks

## Migration Plan
1. Move `services/retriever.py` and `services/rag_orchestrator.py`.
2. Keep existing response schema stable for UI.
3. Add optional hybrid retrieval benchmark before switching defaults.
