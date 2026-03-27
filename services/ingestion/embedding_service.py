from typing import List
import google.generativeai as genai

from apps.api.app.core.config import settings
from packages.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """
    Gemini embeddings service.
    Falls back to a deterministic stub if GEMINI_API_KEY is missing.
    """

    def __init__(self) -> None:
        self.has_real_embeddings = bool(settings.GEMINI_API_KEY)
        if self.has_real_embeddings:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    def _fallback_embedding(self, text: str) -> List[float]:
        text = (text or "").strip()

        if not text:
            return [0.0] * 8

        values = [0.0] * 8
        for i, ch in enumerate(text):
            values[i % 8] += (ord(ch) % 97) / 100.0

        total = sum(values) or 1.0
        return [round(v / total, 6) for v in values]

    def embed_text(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            return []

        if not self.has_real_embeddings:
            logger.warning("GEMINI_API_KEY not set; using fallback embedding.")
            return self._fallback_embedding(text)

        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
            )
            return result["embedding"]
        except Exception as exc:
            logger.exception("Gemini embedding failed, falling back: %s", exc)
            return self._fallback_embedding(text)

    def embed_query(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            return []

        if not self.has_real_embeddings:
            return self._fallback_embedding(text)

        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_query",
            )
            return result["embedding"]
        except Exception as exc:
            logger.exception("Gemini query embedding failed, falling back: %s", exc)
            return self._fallback_embedding(text)