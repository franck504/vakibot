# Ingestion Module

Status: `planned` (logic currently implemented in `services/ingestion.py`, `services/parser.py`, `services/chunker.py`)

## Responsibility
- Receive uploaded documents (`pdf`, `docx`, `txt`).
- Extract clean text from each file.
- Split text into chunks for retrieval.
- Attach metadata (`doc_id`, `filename`, `domain`, `lang`, `chunk_index`).
- Send chunks to embeddings + vector store.

## Expected Files (target structure)
- `loader.py`: ingestion entrypoint
- `parsers/`: file-specific parsers
- `chunking.py`: chunk strategy and windowing
- `pipeline.py`: orchestration and ingestion report

## Migration Plan
1. Move parser helpers from `services/parser.py`.
2. Move chunk logic from `services/chunker.py`.
3. Keep API contract unchanged (`POST /ingest`).
