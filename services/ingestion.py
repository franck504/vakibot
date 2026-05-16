from __future__ import annotations

import mimetypes
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import UploadFile

from core.models import ChunkRecord, IngestResponse
from services.chunker import ChunkingService
from services.embeddings import EmbeddingService
from services.parser import DocumentParserService
from services.vectorstore import VectorStoreService


class IngestionOrchestrator:
    def __init__(self) -> None:
        self.parser = DocumentParserService()
        self.chunker = ChunkingService()
        self.embeddings = EmbeddingService()
        self.vectorstore = VectorStoreService()

    async def ingest_files(
        self,
        files: list[UploadFile],
        domain: str | None = None,
        lang: str | None = None,
    ) -> IngestResponse:
        normalized_domain = (domain or "").strip().lower() or None
        normalized_lang = (lang or "").strip().lower() or None
        errors: list[str] = []
        indexed_document_ids: list[str] = []
        all_chunks: list[ChunkRecord] = []

        for f in files:
            try:
                content = await f.read()
                if not content:
                    raise ValueError("File is empty")

                text = self.parser.parse(content, f.filename or "unknown")
                chunks = self.chunker.split(text)
                if not chunks:
                    raise ValueError("No extractable text found")

                doc_id = str(uuid4())
                indexed_document_ids.append(doc_id)
                mime_type = f.content_type or mimetypes.guess_type(f.filename or "")[0] or "application/octet-stream"

                for idx, chunk_text in enumerate(chunks):
                    all_chunks.append(
                        ChunkRecord(
                            id=f"{doc_id}:{idx}",
                            doc_id=doc_id,
                            chunk_index=idx,
                            text=chunk_text,
                            source=f.filename or "unknown",
                            mime_type=mime_type,
                            filename=f.filename or "unknown",
                            domain=normalized_domain,
                            lang=normalized_lang,
                            created_at=datetime.now(timezone.utc),
                        )
                    )
            except Exception as exc:
                errors.append(f"{f.filename or 'unknown'}: {exc}")

        chunk_count = 0
        if all_chunks:
            embeddings = self.embeddings.embed_texts([c.text for c in all_chunks])
            chunk_count = self.vectorstore.upsert_chunks(all_chunks, embeddings)
        total_chunks = self.vectorstore.count_chunks()

        return IngestResponse(
            status="ok" if not errors else "partial_success",
            documents_received=len(files),
            documents_indexed=len(indexed_document_ids),
            chunks_indexed=chunk_count,
            total_chunks=total_chunks,
            failed_documents=len(files) - len(indexed_document_ids),
            errors=errors,
            indexed_document_ids=indexed_document_ids,
        )
