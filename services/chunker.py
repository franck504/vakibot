from __future__ import annotations


class ChunkingService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        clean = " ".join(text.split())
        if not clean:
            return []

        chunks: list[str] = []
        start = 0
        step = self.chunk_size - self.chunk_overlap

        while start < len(clean):
            end = min(start + self.chunk_size, len(clean))
            chunks.append(clean[start:end])
            if end == len(clean):
                break
            start += step

        return chunks
