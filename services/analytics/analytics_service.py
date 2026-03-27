from typing import List
from packages.types.schemas import AnalyticsResult
from packages.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """
    Temporary stub.
    Later this will call the Rubix dashboard APIs.
    """

    def get_network_summary(self, period: str = "7d") -> List[AnalyticsResult]:
        logger.info("Analytics summary called for period: %s", period)

        return [
            AnalyticsResult(
                metric="transaction_count",
                period=period,
                value=125430,
                notes="Stub value from placeholder analytics service",
            ),
            AnalyticsResult(
                metric="active_wallets",
                period=period,
                value=8421,
                notes="Stub value from placeholder analytics service",
            ),
        ]