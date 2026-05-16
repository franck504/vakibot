from fastapi import APIRouter, File, Form, UploadFile

from core.models import IngestResponse
from services.ingestion import IngestionOrchestrator

router = APIRouter(prefix="", tags=["ingestion"])

orchestrator = IngestionOrchestrator()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    files: list[UploadFile] = File(...),
    domain: str | None = Form(default=None),
    lang: str | None = Form(default=None),
) -> IngestResponse:
    return await orchestrator.ingest_files(files=files, domain=domain, lang=lang)
