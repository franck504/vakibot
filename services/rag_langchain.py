from __future__ import annotations

from core.config import settings
from core.models import QueryResponse
from services.llm_groq import LLMService
from services.rag_common import BaseRAGBehavior
from services.retriever import RetrieverService


class LangChainRAGOrchestrator(BaseRAGBehavior):
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
        try:
            from langchain_core.prompts import PromptTemplate
            from langchain_core.runnables import RunnableLambda
        except Exception as exc:  # noqa: BLE001
            raise ValueError("LangChain engine requested, but langchain is not installed.") from exc

        hits = self.retriever.retrieve(question=question, top_k=top_k, domain=domain, lang=lang)
        if not hits:
            return self.not_found_response()

        max_score = max(float(h.get("score", 0.0)) for h in hits)
        if max_score < settings.retrieval_min_score and not self.allow_low_score_path(question, hits):
            return self.not_found_response()

        context_block, sources = self.build_context_and_sources(hits)

        prompt = PromptTemplate.from_template(
            "Question:\n{question}\n\nContexte:\n{context}\n\nDonne une reponse concise dans la langue de l'utilisateur."
        )

        async def _invoke_llm(rendered_prompt: str) -> str:
            return await self.llm.generate(user_question=question, context_block=rendered_prompt)

        chain = prompt | RunnableLambda(_invoke_llm)
        answer = await chain.ainvoke({"question": question, "context": context_block})

        if not self.is_answer_grounded(answer, sources):
            return self.not_found_response()

        return self.build_success_response(answer=answer, sources=sources, max_score=max_score)
