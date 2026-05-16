from pathlib import Path

import fitz
import pdfplumber
from docx import Document


class DocumentParserService:
    def parse(self, file_bytes: bytes, filename: str) -> str:
        ext = Path(filename).suffix.lower()

        if ext == ".txt":
            return self._parse_txt(file_bytes)
        if ext == ".pdf":
            return self._parse_pdf(file_bytes)
        if ext == ".docx":
            return self._parse_docx(file_bytes)

        raise ValueError(f"Unsupported file extension: {ext}")

    @staticmethod
    def _parse_txt(file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8", errors="ignore")

    @staticmethod
    def _parse_pdf(file_bytes: bytes) -> str:
        text_parts: list[str] = []
        # pdfplumber handles layout text better; fallback to PyMuPDF if needed.
        try:
            import io

            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
        except Exception:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text_parts.append(page.get_text("text") or "")

        return "\n".join(text_parts).strip()

    @staticmethod
    def _parse_docx(file_bytes: bytes) -> str:
        import io

        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text).strip()
