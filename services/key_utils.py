from __future__ import annotations


def parse_api_keys(raw_keys: str, single_key: str) -> list[str]:
    keys: list[str] = []
    if raw_keys.strip():
        keys.extend([k.strip() for k in raw_keys.split(",") if k.strip()])
    if single_key.strip():
        keys.append(single_key.strip())

    deduped: list[str] = []
    for key in keys:
        if key not in deduped:
            deduped.append(key)
    return deduped

