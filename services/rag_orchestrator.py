from __future__ import annotations

import re

from core.config import settings
from core.models import QueryResponse, SourceItem
from services.llm_groq import LLMService
from services.retriever import RetrieverService
from services.text_utils import normalize_text


class RAGOrchestrator:
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

    def __init__(self) -> None:
        self.retriever = RetrieverService()
        self.llm = LLMService()

    async def answer(
        self,
        question: str,
        top_k: int | None = None,
        domain: str | None = None,
        lang: str | None = None,
    ) -> QueryResponse:
        hits = self.retriever.retrieve(question=question, top_k=top_k, domain=domain, lang=lang)

        if not hits:
            return self._not_found_response()

        max_score = max(float(h.get("score", 0.0)) for h in hits)
        if max_score < settings.retrieval_min_score and not self._allow_low_score_path(question, hits):
            return self._not_found_response()

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

        answer = await self.llm.generate(user_question=question, context_block="\n\n".join(context_lines))
        if not self._is_answer_grounded(answer, sources):
            return self._not_found_response()

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

    def _not_found_response(self) -> QueryResponse:
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

    def _is_answer_grounded(self, answer: str, sources: list[SourceItem]) -> bool:
        if not re.search(r"\[S\d+\]", answer):
            return False

        normalized_answer = normalize_text(answer)
        for marker in self.SPECULATIVE_MARKERS:
            if marker in normalized_answer:
                return False

        source_corpus = normalize_text(" ".join(s.excerpt for s in sources))
        source_tokens = set(source_corpus.split())
        answer_tokens = [t for t in normalize_text(re.sub(r"\[S\d+\]", " ", answer)).split() if len(t) > 3]
        if not answer_tokens:
            return False

        overlap = sum(1 for t in answer_tokens if t in source_tokens) / len(answer_tokens)
        return overlap >= 0.15

    def _allow_low_score_path(self, question: str, hits: list[dict]) -> bool:
        q = normalize_text(question)
        has_trigger = any(t in q for t in self.LEGAL_TRIGGERS)
        has_min_hit = any(float(h.get("score", 0.0)) >= 0.10 for h in hits)
        return has_trigger and has_min_hit
