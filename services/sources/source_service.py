from sqlalchemy.orm import Session

from packages.db.models import Source, DocumentChunk
from packages.utils.logger import get_logger
from services.ingestion.chunking import TextChunker
from services.ingestion.embedding_service import EmbeddingService

logger = get_logger(__name__)


class SourceService:
    def __init__(self) -> None:
        self.chunker = TextChunker()
        self.embedding_service = EmbeddingService()

    def list_sources(self, db: Session) -> list[Source]:
        return (
            db.query(Source)
            .order_by(Source.created_at.desc())
            .all()
        )

    def get_source(self, db: Session, source_id: str) -> Source | None:
        return (
            db.query(Source)
            .filter(Source.id == source_id)
            .first()
        )

    def get_source_chunks(self, db: Session, source_id: str) -> list[DocumentChunk]:
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.source_id == source_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )

    def delete_source(self, db: Session, source_id: str) -> bool:
        source = self.get_source(db, source_id)
        if not source:
            return False

        db.delete(source)
        db.commit()

        logger.info("Deleted source: %s", source_id)
        return True

    def reindex_source(self, db: Session, source_id: str) -> tuple[bool, int]:
        source = self.get_source(db, source_id)
        if not source:
            return False, 0

        old_chunks = self.get_source_chunks(db, source_id)
        for chunk in old_chunks:
            db.delete(chunk)

        db.flush()

        chunks = self.chunker.chunk_text(source.raw_text)

        for idx, chunk_text in enumerate(chunks):
            embedding = self.embedding_service.embed_text(chunk_text)

            chunk = DocumentChunk(
                source_id=source.id,
                chunk_index=idx,
                section_title=None,
                chunk_text=chunk_text,
                token_count=len(chunk_text.split()),
                embedding_json=embedding,
                embedding=embedding,
            )
            db.add(chunk)

        db.commit()

        logger.info("Reindexed source %s with %s chunks", source_id, len(chunks))
        return True, len(chunks)