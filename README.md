# VakiBot

Assistant juridique documentaire (RAG), déployé en mode Docker-first.

## Objectif
- Indexer des documents juridiques (`pdf`, `docx`, `txt`).
- Répondre uniquement depuis les sources indexées.
- Réduire les hallucinations via fallback strict et citations.

## Stack
- API: FastAPI
- Vector DB: Chroma
- LLM: Groq API (distant)
- Embeddings: Jina API (avec fallback local)
- Runtime: Docker Compose

## Architecture (projet portfolio)

```text
vakibot/
├── api/              # Entrypoint HTTP, routes, middleware, gestion erreurs
├── core/             # Config centralisée + modèles de données
├── services/         # Implémentation active actuelle (v1)
├── ingestion/        # Module cible dédié ingestion (planned)
├── rag/              # Module cible dédié retrieval/generation (planned)
├── evaluation/       # Module cible évaluation qualité (planned)
├── ui/               # Module cible interface (in_progress)
├── data/             # Datasets/samples locaux (sans données sensibles)
├── guides/           # Feuilles de route (code/ui/complet)
└── storage/          # Données vector store persistées
```

## Statut des modules
- `api/`: actif
- `core/`: actif
- `services/`: actif (coeur fonctionnel v1)
- `ingestion/`: planned (README présent)
- `rag/`: planned (README présent)
- `evaluation/`: planned (README présent)
- `ui/`: in_progress (README présent)
- `data/`: in_use (README présent)

## Démarrage rapide (Docker)

### Prérequis
- Docker
- Docker Compose

### Commandes
1. `sudo systemctl start docker`
2. `export DOCKER_HOST=unix:///var/run/docker.sock`
3. `docker compose build`
4. `docker compose up -d`

## Vérification
- API health: `curl http://localhost:8000/health`
- Chroma heartbeat: `curl http://localhost:8001/api/v2/heartbeat`
- UI: `http://localhost:8000/`

## Variables d'environnement clés
- `GROQ_API_KEY` ou `GROQ_API_KEYS`
- `GROQ_MODEL`
- `EMBEDDING_API_KEY` ou `EMBEDDING_API_KEYS`
- `EMBEDDING_BASE_URL`
- `EMBEDDING_MODEL`
- `RETRIEVAL_MIN_SCORE`
- `TOP_K_DEFAULT`
- `MAX_CONTEXT_CHUNKS`

Voir `.env.example` pour le template complet.

## Qualité / garde-fous
- Réponse basée sur sources uniquement
- Vérification citations `[Sx]`
- Fallback si retrieval insuffisant
- Message d'échec explicite + suggestions de reformulation

## Roadmap de structuration (pro)
1. Migrer progressivement `services/parser.py`, `services/chunker.py`, `services/ingestion.py` vers `ingestion/`.
2. Migrer `services/retriever.py`, `services/rag_orchestrator.py`, `services/llm_groq.py` vers `rag/`.
3. Ajouter un mini framework d'évaluation dans `evaluation/` (jeu de tests + métriques).
4. Extraire l'UI inline de `api/routers/ui.py` vers `ui/` (`templates`, `static/css`, `static/js`) sans casser les endpoints.

## Arrêt
- `docker compose down`
