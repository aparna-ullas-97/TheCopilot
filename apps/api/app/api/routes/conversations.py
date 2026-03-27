from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.db.database import get_db
from packages.types.schemas import (
    ConversationDetailResponse,
    ConversationItem,
    MessageItem,
)
from services.conversations.conversation_service import ConversationService

router = APIRouter()
conversation_service = ConversationService()


@router.get("/conversations", response_model=list[ConversationItem])
def list_conversations(db: Session = Depends(get_db)):
    conversations = conversation_service.list_conversations(db)

    return [
        ConversationItem(
            id=item.id,
            title=item.title,
            created_at=item.created_at.isoformat(),
            updated_at=item.updated_at.isoformat(),
        )
        for item in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation, messages = conversation_service.get_conversation_with_messages(
        db=db,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationDetailResponse(
        conversation=ConversationItem(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
        ),
        messages=[
            MessageItem(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                sources_used_json=msg.sources_used_json,
                created_at=msg.created_at.isoformat(),
            )
            for msg in messages
        ],
    )

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    success = conversation_service.delete_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted"}