from abc import ABC, abstractmethod
from typing import List

from packages.types.schemas import SourceItem, AnalyticsResult


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        user_message: str,
        sources: List[SourceItem],
        analytics: List[AnalyticsResult],
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        raise NotImplementedError