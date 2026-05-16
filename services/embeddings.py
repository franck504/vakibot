from __future__ import annotations

import hashlib
import logging
import time

import httpx

from core.config import settings
from services.key_utils import parse_api_keys

logger = logging.getLogger("vakibot.embeddings")


class EmbeddingService:
    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        api_keys = parse_api_keys(settings.embedding_api_keys, settings.embedding_api_key)
        if api_keys:
            try:
                return self._embed_via_api(texts, api_keys)
            except Exception as exc:
                logger.warning("Embedding API failed, fallback local embeddings: %s", exc)
        return [self._fallback_embed_one(text) for text in texts]

    def _embed_via_api(self, texts: list[str], api_keys: list[str]) -> list[list[float]]:
        payload = {"model": settings.embedding_model, "input": texts}
        last_error: Exception | None = None
        for key in api_keys:
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            }
            for attempt in range(3):
                try:
                    with httpx.Client(timeout=60.0) as client:
                        response = client.post(f"{settings.embedding_base_url}/embeddings", headers=headers, json=payload)
                    if response.status_code == 429:
                        raise httpx.HTTPStatusError("rate limited", request=response.request, response=response)
                    response.raise_for_status()
                    data = response.json()
                    vectors = [item["embedding"] for item in data.get("data", [])]
                    if not vectors:
                        raise ValueError("Embedding API returned no vectors")
                    return vectors
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
                    if attempt < 2:
                        time.sleep(0.6 * (attempt + 1))
                    continue
        raise ValueError(f"All embedding API keys failed: {last_error}")

    def _fallback_embed_one(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
        vec = [0.0] * self.dimensions
        for i in range(self.dimensions):
            vec[i] = ((digest[i % len(digest)] / 255.0) * 2.0) - 1.0
        return vec
