from __future__ import annotations

import re

import chromadb
from chromadb.api import ClientAPI

from core.config import settings
from core.models import ChunkRecord


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "_", value)
    return cleaned[:48]


class VectorStoreService:
    def __init__(self, collection_name: str | None = None) -> None:
        self.client: ClientAPI = chromadb.PersistentClient(path=settings.chroma_persist_dir)

        if collection_name:
            final_name = collection_name
        else:
            model_tag = _safe_name(settings.embedding_model)
            final_name = f"vakibot_docs_{model_tag}"

        self.collection = self.client.get_or_create_collection(name=final_name)

    def upsert_chunks(self, chunks: list[ChunkRecord], embeddings: list[list[float]]) -> int:
        ids = [c.id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [
            {
                "doc_id": c.doc_id,
                "chunk_index": c.chunk_index,
                "source": c.source,
                "mime_type": c.mime_type,
                "filename": c.filename,
                "domain": c.domain or "",
                "lang": c.lang or "",
                "created_at": c.created_at.isoformat(),
            }
            for c in chunks
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return len(chunks)

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        domain: str | None = None,
        lang: str | None = None,
    ) -> list[dict]:
        where = self._build_where(domain=domain, lang=lang)

        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["metadatas", "documents", "distances"],
        )

        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]

        hits: list[dict] = []
        for idx, item_id in enumerate(ids):
            meta = metas[idx] if idx < len(metas) else {}
            dist = float(dists[idx]) if idx < len(dists) else 1.0
            score = max(0.0, 1.0 - dist)
            hits.append(
                {
                    "id": item_id,
                    "document": docs[idx] if idx < len(docs) else "",
                    "metadata": meta,
                    "distance": dist,
                    "score": score,
                }
            )
        return hits

    def list_sources(
        self,
        limit: int = 50,
        domain: str | None = None,
        lang: str | None = None,
        filename: str | None = None,
        doc_id: str | None = None,
    ) -> list[dict]:
        where = self._build_where(domain=domain, lang=lang, filename=filename, doc_id=doc_id)

        result = self.collection.get(
            where=where,
            limit=limit,
            include=["metadatas", "documents"],
        )

        ids = result.get("ids", [])
        metas = result.get("metadatas", [])
        docs = result.get("documents", [])

        rows: list[dict] = []
        for idx, item_id in enumerate(ids):
            meta = metas[idx] if idx < len(metas) else {}
            doc = docs[idx] if idx < len(docs) else ""
            rows.append(
                {
                    "id": item_id,
                    "metadata": meta,
                    "document": doc,
                }
            )
        return rows

    def delete_document(self, doc_id: str) -> int:
        rows = self.list_sources(limit=100000, doc_id=doc_id)
        ids = [r["id"] for r in rows]
        if not ids:
            return 0
        self.collection.delete(ids=ids)
        return len(ids)

    def count_chunks(self) -> int:
        return int(self.collection.count())

    @staticmethod
    def _build_where(
        domain: str | None = None,
        lang: str | None = None,
        filename: str | None = None,
        doc_id: str | None = None,
    ) -> dict | None:
        domain = (domain or "").strip().lower() or None
        lang = (lang or "").strip().lower() or None
        filename = (filename or "").strip() or None
        doc_id = (doc_id or "").strip() or None

        clauses: list[dict] = []
        if domain:
            clauses.append({"domain": {"$eq": domain}})
        if lang:
            clauses.append({"lang": {"$eq": lang}})
        if filename:
            clauses.append({"filename": {"$eq": filename}})
        if doc_id:
            clauses.append({"doc_id": {"$eq": doc_id}})

        if not clauses:
            return None
        if len(clauses) == 1:
            return clauses[0]
        return {"$and": clauses}
