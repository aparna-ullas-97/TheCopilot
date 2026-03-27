from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.db.database import get_db
from packages.types.schemas import ChatRequest, ChatResponse
from services.orchestration.chat_orchestrator import ChatOrchestrator

router = APIRouter()
orchestrator = ChatOrchestrator()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        return orchestrator.handle_chat(db=db, request=request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc