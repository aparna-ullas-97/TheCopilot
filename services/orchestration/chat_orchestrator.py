from sqlalchemy.orm import Session

from packages.types.schemas import ChatRequest, ChatResponse
from packages.utils.citations import normalize_inline_citations
from packages.utils.logger import get_logger
from services.analytics.analytics_service import AnalyticsService
from services.conversations.conversation_service import ConversationService
from services.llm.factory import get_llm_provider
from services.retrieval.retrieval_service import RetrievalService

logger = get_logger(__name__)


class ChatOrchestrator:
    def __init__(self) -> None:
        self.retrieval = RetrievalService()
        self.analytics = AnalyticsService()
        self.llm = get_llm_provider()
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
            answer = self.llm.generate(
                user_message=request.message,
                sources=sources,
                analytics=analytics,
                temperature=0.2,
                max_tokens=400,
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
                "model": getattr(self.llm, "provider_name", "unknown"),
            },
        )