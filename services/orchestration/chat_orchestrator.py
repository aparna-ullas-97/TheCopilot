from sqlalchemy.orm import Session

from packages.types.schemas import ChatRequest, ChatResponse
from packages.utils.logger import get_logger
from packages.utils.citations import normalize_inline_citations
from services.retrieval.retrieval_service import RetrievalService
from services.analytics.analytics_service import AnalyticsService
from services.llm.gemini_adapter import GeminiAdapter
from services.conversations.conversation_service import ConversationService

logger = get_logger(__name__)


class ChatOrchestrator:
    def __init__(self) -> None:
        self.retrieval = RetrievalService()
        self.analytics = AnalyticsService()
        self.llm = GeminiAdapter()
        self.conversations = ConversationService()

    def _classify_intent(self, message: str) -> str:
        msg = message.lower()

        analytics_keywords = [
            "transaction",
            "transactions",
            "wallet",
            "volume",
            "analytics",
            "network",
            "on-chain",
            "onchain",
            "contract",
        ]

        if any(keyword in msg for keyword in analytics_keywords):
            return "hybrid"

        return "knowledge"

    def handle_chat(self, db: Session, request: ChatRequest) -> ChatResponse:
        logger.info("Handling chat request")

        conversation = self.conversations.get_or_create_conversation(
            db=db,
            conversation_id=request.conversation_id,
            title=request.message[:60],
        )

        self.conversations.save_message(
            db=db,
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )

        intent = self._classify_intent(request.message)
        sources = self.retrieval.search(db=db, query=request.message)
        analytics = []

        strong_sources = [s for s in sources if (s.score or 0) >= 0.35]

        if not strong_sources and not analytics:
            answer = "I don’t have enough grounded information to answer that yet."
        else:
            answer = self.llm.generate_answer(
                user_message=request.message,
                sources=sources,
                analytics=analytics,
            )
            answer = normalize_inline_citations(answer)

        self.conversations.save_message(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            sources_used=sources,
        )

        return ChatResponse(
            answer=answer,
            conversation_id=conversation.id,
            sources=sources,
            analytics=analytics,
            meta={
                "intent": intent,
                "model": "gemini",
            },
        )