from fastapi import APIRouter, HTTPException, status

from core.config import settings
from core.models import QueryRequest, QueryResponse
from services.rag_langchain import LangChainRAGOrchestrator
from services.rag_orchestrator import RAGOrchestrator

router = APIRouter(prefix="", tags=["query"])

orchestrator_diy = RAGOrchestrator()
orchestrator_langchain = LangChainRAGOrchestrator()


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest) -> QueryResponse:
    engine = (payload.engine or settings.rag_engine or "diy").strip().lower()
    if engine not in {"diy", "langchain"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid engine. Use 'diy' or 'langchain'.",
        )

    orchestrator = orchestrator_langchain if engine == "langchain" else orchestrator_diy

    try:
        return await orchestrator.answer(
            question=payload.question,
            top_k=payload.top_k,
            domain=payload.domain,
            lang=payload.lang,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
