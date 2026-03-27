from pathlib import Path
from pypdf import PdfReader
from docx import Document

from packages.utils.logger import get_logger

logger = get_logger(__name__)


class FileExtractor:
    SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

    def extract(self, file_path: str) -> tuple[str, str]:
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")

        if ext in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            return path.stem, text

        if ext == ".pdf":
            return path.stem, self._extract_pdf(path)

        if ext == ".docx":
            return path.stem, self._extract_docx(path)

        raise ValueError(f"Unsupported file type: {ext}")

    def _extract_pdf(self, path: Path) -> str:
        logger.info("Extracting PDF: %s", path)
        reader = PdfReader(str(path))
        pages = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text.strip())

        return "\n\n".join(pages)

    def _extract_docx(self, path: Path) -> str:
        logger.info("Extracting DOCX: %s", path)
        doc = Document(str(path))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)