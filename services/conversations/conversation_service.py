from datetime import datetime
from sqlalchemy.orm import Session

from packages.db.models import Conversation, Message
from packages.types.schemas import SourceItem
from packages.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationService:
    def get_or_create_conversation(
        self,
        db: Session,
        conversation_id: str | None = None,
        title: str | None = None,
    ) -> Conversation:
        if conversation_id:
            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )
            if conversation:
                return conversation

        conversation = Conversation(
            title=title or "New Chat",
            updated_at=datetime.utcnow(),
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        logger.info("Created conversation: %s", conversation.id)
        return conversation

    def save_message(
        self,
        db: Session,
        *,
        conversation_id: str,
        role: str,
        content: str,
        sources_used: list[SourceItem] | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources_used_json=[s.model_dump() for s in sources_used] if sources_used else None,
        )
        db.add(message)

        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
        if conversation:
            conversation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(message)

        logger.info("Saved %s message for conversation %s", role, conversation_id)
        return message

    def list_conversations(self, db: Session) -> list[Conversation]:
        return (
            db.query(Conversation)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    def get_conversation_with_messages(
        self,
        db: Session,
        conversation_id: str,
    ) -> tuple[Conversation | None, list[Message]]:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

        if not conversation:
            return None, []

        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )

        return conversation, messages
    

    def delete_conversation(self, db: Session, conversation_id: str) -> bool:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

        if not conversation:
            return False

        db.delete(conversation)
        db.commit()

        logger.info("Deleted conversation: %s", conversation_id)
        return True