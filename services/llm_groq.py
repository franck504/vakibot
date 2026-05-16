from __future__ import annotations

import asyncio
import httpx

from core.config import settings
from services.exceptions import UpstreamRateLimitError, UpstreamServiceError
from services.key_utils import parse_api_keys


class LLMService:
    async def generate(self, user_question: str, context_block: str) -> str:
        api_keys = parse_api_keys(settings.groq_api_keys, settings.groq_api_key)
        if not api_keys:
            raise ValueError("Missing GROQ_API_KEY or GROQ_API_KEYS in environment")

        system_prompt = (
            "Tu es VakiBot, assistant juridique documentaire strict. "
            "Interdiction absolue d'ajouter des informations hors contexte fourni. "
            "Chaque affirmation doit être soutenue par citation [Sx]. "
            "Si le contexte est insuffisant, réponds EXACTEMENT d'abord: "
            "\"Je ne dispose pas d'éléments suffisamment explicites pour répondre avec certitude.\" "
            "Puis ajoute une section \"Suggestions utiles:\" avec 2-4 formulations courtes. "
            "N'invente jamais de loi, de durée, ni de déduction."
        )

        user_prompt = (
            f"Question:\n{user_question}\n\n"
            f"Contexte:\n{context_block}\n\n"
            "Donne une reponse concise dans la langue de l'utilisateur."
        )

        payload = {
            "model": settings.groq_model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        last_error: Exception | None = None
        for key_index, api_key in enumerate(api_keys):
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            for attempt in range(3):
                try:
                    async with httpx.AsyncClient(timeout=45.0) as client:
                        response = await client.post(
                            f"{settings.groq_base_url}/chat/completions",
                            headers=headers,
                            json=payload,
                        )
                    if response.status_code == 429:
                        raise UpstreamRateLimitError("Groq rate limit reached")
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
                except UpstreamRateLimitError as exc:
                    last_error = exc
                    # Try next key quickly; on same key, short backoff.
                    if attempt < 2:
                        await asyncio.sleep(0.8 * (attempt + 1))
                    continue
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
                    if attempt < 2:
                        await asyncio.sleep(0.5 * (attempt + 1))
                    continue
            # move to next key
            if key_index < len(api_keys) - 1:
                await asyncio.sleep(0.2)

        if isinstance(last_error, UpstreamRateLimitError):
            raise UpstreamRateLimitError("All Groq API keys are rate-limited. Retry in a moment.")
        raise UpstreamServiceError(f"Groq upstream error: {last_error}")
