from __future__ import annotations

import re
import unicodedata


def normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    no_accents = "".join(c for c in unicodedata.normalize("NFD", lowered) if unicodedata.category(c) != "Mn")
    no_punct = re.sub(r"[^a-z0-9\s]", " ", no_accents)
    compact = re.sub(r"\s+", " ", no_punct).strip()
    return compact


def expand_short_legal_query(question: str) -> str:
    normalized = normalize_text(question)
    if len(normalized.split()) <= 2:
        return f"{question} dans le contexte du code penal malgache et des sanctions"
    return question


def extract_article_number(question: str) -> int | None:
    lowered = question.lower()
    m = re.search(r"(?:article|art\.?)\s*(\d{1,4})", lowered)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None
