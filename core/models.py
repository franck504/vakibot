from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    service: str
    version: str
    environment: str


class ErrorResponse(BaseModel):
    error: str
    detail: str
    code: str


class IngestResponse(BaseModel):
    status: str
    documents_received: int
    documents_indexed: int
    chunks_indexed: int
    total_chunks: int
    failed_documents: int
    errors: list[str]
    indexed_document_ids: list[str]


class ChunkRecord(BaseModel):
    id: str
    doc_id: str
    chunk_index: int
    text: str
    source: str
    mime_type: str
    filename: str
    domain: str | None = None
    lang: str | None = None
    created_at: datetime


class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int | None = Field(default=None, ge=1, le=20)
    domain: str | None = None
    lang: str | None = None
    engine: Literal["diy", "langchain"] | None = None


class SourceItem(BaseModel):
    source_id: str
    doc_id: str
    filename: str
    chunk_index: int
    excerpt: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    model: str
    sources: list[SourceItem]
    retrieval_count: int
    avg_score: float = 0.0
    max_score: float = 0.0
    confidence: str = "low"


class SourceListItem(BaseModel):
    id: str
    doc_id: str
    filename: str
    chunk_index: int
    domain: str | None = None
    lang: str | None = None
    excerpt: str


class SourceListResponse(BaseModel):
    count: int
    sources: list[SourceListItem]


class DeleteDocumentResponse(BaseModel):
    status: str
    doc_id: str
    deleted_chunks: int
