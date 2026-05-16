from __future__ import annotations

import re

from core.config import settings
from core.models import QueryResponse, SourceItem
from services.text_utils import normalize_text


class BaseRAGBehavior:
    SPECULATIVE_MARKERS = [
        "on peut deduire",
        "on peut en deduire",
        "on peut conclure",
        "donc la duree",
        "probablement",
        "generalement",
        "en pratique",
        "il est possible que",
    ]
    LEGAL_TRIGGERS = [
        "article",
        "art",
        "prescription",
        "viol",
        "vol",
        "complicite",
        "travaux forces",
        "peine",
        "sanction",
    ]

    @staticmethod
    def not_found_response() -> QueryResponse:
        return QueryResponse(
            answer=(
                "Je ne dispose pas d'éléments suffisamment explicites pour répondre avec certitude.\n\n"
                "Suggestions utiles:\n"
                "- Préciser l'infraction, le contexte ou la période.\n"
                "- Mentionner un article ou une section (ex: \"article 463\").\n"
                "- Ajouter des mots-clés juridiques proches (qualification, peine, prescription, procédure).\n"
                "- Vérifier les filtres actifs (domain/lang) ou augmenter top_k."
            ),
            model=settings.groq_model,
            sources=[],
            retrieval_count=0,
            avg_score=0.0,
            max_score=0.0,
            confidence="low",
        )

    @staticmethod
    def build_context_and_sources(hits: list[dict]) -> tuple[str, list[SourceItem]]:
        context_lines: list[str] = []
        sources: list[SourceItem] = []

        for idx, hit in enumerate(hits[: settings.max_context_chunks], start=1):
            meta = hit.get("metadata", {})
            excerpt = (hit.get("document") or "")[:1200]
            source_tag = f"S{idx}"
            context_lines.append(f"[{source_tag}] {excerpt}")
            sources.append(
                SourceItem(
                    source_id=source_tag,
                    doc_id=str(meta.get("doc_id", "")),
                    filename=str(meta.get("filename", meta.get("source", "unknown"))),
                    chunk_index=int(meta.get("chunk_index", 0)),
                    excerpt=excerpt,
                    score=float(hit.get("score", 0.0)),
                )
            )
        return "\n\n".join(context_lines), sources

    @classmethod
    def is_answer_grounded(cls, answer: str, sources: list[SourceItem]) -> bool:
        if not re.search(r"\[S\d+\]", answer):
            return False

        normalized_answer = normalize_text(answer)
        for marker in cls.SPECULATIVE_MARKERS:
            if marker in normalized_answer:
                return False

        source_corpus = normalize_text(" ".join(s.excerpt for s in sources))
        source_tokens = set(source_corpus.split())
        answer_tokens = [t for t in normalize_text(re.sub(r"\[S\d+\]", " ", answer)).split() if len(t) > 3]
        if not answer_tokens:
            return False

        overlap = sum(1 for t in answer_tokens if t in source_tokens) / len(answer_tokens)
        return overlap >= 0.15

    @classmethod
    def allow_low_score_path(cls, question: str, hits: list[dict]) -> bool:
        q = normalize_text(question)
        has_trigger = any(t in q for t in cls.LEGAL_TRIGGERS)
        has_min_hit = any(float(h.get("score", 0.0)) >= 0.10 for h in hits)
        return has_trigger and has_min_hit

    @staticmethod
    def build_success_response(answer: str, sources: list[SourceItem], max_score: float) -> QueryResponse:
        avg_score = sum(float(s.score) for s in sources) / max(1, len(sources))
        confidence = "low" if avg_score < settings.retrieval_min_score else "medium"
        return QueryResponse(
            answer=answer,
            model=settings.groq_model,
            sources=sources,
            retrieval_count=len(sources),
            avg_score=avg_score,
            max_score=max_score,
            confidence=confidence,
        )

