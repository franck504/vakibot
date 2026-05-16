from fastapi import APIRouter, HTTPException, Query, status

from core.models import DeleteDocumentResponse, SourceListItem, SourceListResponse
from services.vectorstore import VectorStoreService

router = APIRouter(prefix="", tags=["sources"])
vectorstore = VectorStoreService()


@router.get("/sources", response_model=SourceListResponse)
def list_sources(
    limit: int = Query(default=50, ge=1, le=200),
    domain: str | None = None,
    lang: str | None = None,
    filename: str | None = None,
) -> SourceListResponse:
    rows = vectorstore.list_sources(limit=limit, domain=domain, lang=lang, filename=filename)

    sources = [
        SourceListItem(
            id=r["id"],
            doc_id=str(r["metadata"].get("doc_id", "")),
            filename=str(r["metadata"].get("filename", "unknown")),
            chunk_index=int(r["metadata"].get("chunk_index", 0)),
            domain=(r["metadata"].get("domain") or None),
            lang=(r["metadata"].get("lang") or None),
            excerpt=(r.get("document") or "")[:400],
        )
        for r in rows
    ]

    return SourceListResponse(count=len(sources), sources=sources)


@router.delete("/documents/{doc_id}", response_model=DeleteDocumentResponse)
def delete_document(doc_id: str) -> DeleteDocumentResponse:
    deleted = vectorstore.delete_document(doc_id)
    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {doc_id}",
        )
    return DeleteDocumentResponse(status="ok", doc_id=doc_id, deleted_chunks=deleted)
