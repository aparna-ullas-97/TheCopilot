from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.db.database import get_db
from packages.types.schemas import (
    SourceListItem,
    SourceDetailResponse,
    SourceChunksResponse,
    ChunkItem,
    DeleteResponse,
    ReindexResponse,
)
from services.sources.source_service import SourceService

router = APIRouter()
source_service = SourceService()


@router.get("/sources", response_model=list[SourceListItem])
def list_sources(db: Session = Depends(get_db)):
    sources = source_service.list_sources(db)

    result = []
    for source in sources:
        chunk_count = len(source.chunks) if source.chunks else 0
        result.append(
            SourceListItem(
                id=source.id,
                source_type=source.source_type,
                title=source.title,
                source_url=source.source_url,
                author=source.author,
                trust_level=source.trust_level,
                created_at=source.created_at.isoformat(),
                chunk_count=chunk_count,
            )
        )

    return result


@router.get("/sources/{source_id}", response_model=SourceDetailResponse)
def get_source(source_id: str, db: Session = Depends(get_db)):
    source = source_service.get_source(db, source_id)

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    return SourceDetailResponse(
        id=source.id,
        source_type=source.source_type,
        title=source.title,
        source_url=source.source_url,
        author=source.author,
        trust_level=source.trust_level,
        raw_text=source.raw_text,
        metadata_json=source.metadata_json,
        created_at=source.created_at.isoformat(),
        chunk_count=len(source.chunks) if source.chunks else 0,
    )


@router.get("/sources/{source_id}/chunks", response_model=SourceChunksResponse)
def get_source_chunks(source_id: str, db: Session = Depends(get_db)):
    source = source_service.get_source(db, source_id)

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    chunks = source_service.get_source_chunks(db, source_id)

    return SourceChunksResponse(
        source_id=source.id,
        title=source.title,
        chunks=[
            ChunkItem(
                id=chunk.id,
                source_id=chunk.source_id,
                chunk_index=chunk.chunk_index,
                section_title=chunk.section_title,
                chunk_text=chunk.chunk_text,
                token_count=chunk.token_count,
                created_at=chunk.created_at.isoformat(),
            )
            for chunk in chunks
        ],
    )


@router.delete("/sources/{source_id}", response_model=DeleteResponse)
def delete_source(source_id: str, db: Session = Depends(get_db)):
    success = source_service.delete_source(db, source_id)

    if not success:
        raise HTTPException(status_code=404, detail="Source not found")

    return DeleteResponse(message="Source deleted successfully")


@router.post("/sources/{source_id}/reindex", response_model=ReindexResponse)
def reindex_source(source_id: str, db: Session = Depends(get_db)):
    success, chunk_count = source_service.reindex_source(db, source_id)

    if not success:
        raise HTTPException(status_code=404, detail="Source not found")

    return ReindexResponse(
        source_id=source_id,
        chunk_count=chunk_count,
        message="Source reindexed successfully",
    )