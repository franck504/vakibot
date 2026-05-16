from fastapi import APIRouter, HTTPException, status

from core.models import QueryRequest, QueryResponse
from services.rag_orchestrator import RAGOrchestrator

router = APIRouter(prefix="", tags=["query"])

orchestrator = RAGOrchestrator()


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest) -> QueryResponse:
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
