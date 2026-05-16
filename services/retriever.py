from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from core.config import settings
from services.embeddings import EmbeddingService
from services.text_utils import expand_short_legal_query, extract_article_number, normalize_text
from services.vectorstore import VectorStoreService


class RetrieverService:
    def __init__(self) -> None:
        self.embedder = EmbeddingService()
        self.vectorstore = VectorStoreService()

    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
        domain: str | None = None,
        lang: str | None = None,
    ) -> list[dict]:
        k = top_k or settings.top_k_default
        if settings.strict_legal_mode:
            domain = domain or settings.legal_default_domain
        expanded_question = expand_short_legal_query(question)
        article_num = extract_article_number(question)

        vector_hits = self._vector_search(expanded_question, max(k * 3, 10), domain, lang)
        if settings.retrieval_mode != "hybrid":
            boosted = self._apply_legal_boost(vector_hits, article_num, expanded_question)
            return boosted[:k]

        bm25_hits = self._bm25_search(expanded_question, max(k * 3, 10), domain, lang)
        merged = self._fuse_hits(vector_hits, bm25_hits, k * 3)
        boosted = self._apply_legal_boost(merged, article_num, expanded_question)
        return boosted[:k]

    def _vector_search(self, question: str, top_k: int, domain: str | None, lang: str | None) -> list[dict]:
        query_embedding = self.embedder.embed_texts([question])[0]
        return self.vectorstore.search(query_embedding=query_embedding, top_k=top_k, domain=domain, lang=lang)

    def _bm25_search(self, question: str, top_k: int, domain: str | None, lang: str | None) -> list[dict]:
        rows = self.vectorstore.list_sources(limit=2000, domain=domain, lang=lang)
        if not rows:
            return []
        if settings.strict_legal_mode:
            hint = normalize_text(settings.legal_filename_hint)
            rows = [r for r in rows if hint in normalize_text(str(r.get("metadata", {}).get("filename", "")))]
            if not rows:
                return []

        documents = [r.get("document") or "" for r in rows]
        tokenized_docs = [normalize_text(doc).split() for doc in documents]
        tokenized_docs = [toks if toks else ["_"] for toks in tokenized_docs]

        bm25 = BM25Okapi(tokenized_docs)
        q_tokens = normalize_text(question).split() or ["_"]
        scores = bm25.get_scores(q_tokens)

        indexed = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        max_score = max((s for _, s in indexed), default=1.0) or 1.0

        hits: list[dict] = []
        for idx, raw_score in indexed:
            row = rows[idx]
            hits.append(
                {
                    "id": row["id"],
                    "document": row.get("document", ""),
                    "metadata": row.get("metadata", {}),
                    "distance": 1.0,
                    "score": float(raw_score / max_score),
                }
            )
        return hits

    def _fuse_hits(self, vector_hits: list[dict], bm25_hits: list[dict], k: int) -> list[dict]:
        fused: dict[str, dict] = {}

        for hit in vector_hits:
            hid = hit["id"]
            fused[hid] = {**hit, "score": settings.hybrid_vector_weight * float(hit.get("score", 0.0))}

        for hit in bm25_hits:
            hid = hit["id"]
            bm_score = settings.hybrid_bm25_weight * float(hit.get("score", 0.0))
            if hid in fused:
                fused[hid]["score"] += bm_score
            else:
                fused[hid] = {**hit, "score": bm_score}

        merged = sorted(fused.values(), key=lambda x: float(x.get("score", 0.0)), reverse=True)
        return merged[:k]

    def _apply_legal_boost(self, hits: list[dict], article_num: int | None, question: str) -> list[dict]:
        q_norm = normalize_text(question)
        for hit in hits:
            score = float(hit.get("score", 0.0))
            doc_norm = normalize_text(hit.get("document", ""))

            if article_num is not None:
                if re.search(rf"\bart\s*{article_num}\b", doc_norm) or re.search(
                    rf"\barticle\s*{article_num}\b", doc_norm
                ):
                    score += 0.35

            if "prescription" in q_norm and "prescription" in doc_norm:
                score += 0.15
            if "viol" in q_norm and "viol" in doc_norm:
                score += 0.15
            if "travaux forces" in q_norm and "travaux forces" in doc_norm:
                score += 0.15

            hit["score"] = score

        return sorted(hits, key=lambda x: float(x.get("score", 0.0)), reverse=True)
