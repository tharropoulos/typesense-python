"""Client for Typesense Analytics module (async)."""

from typesense.async_analytics_events import AsyncAnalyticsEvents
from typesense.async_analytics_rules import AsyncAnalyticsRules
from typesense.async_api_call import AsyncApiCall


class AsyncAnalytics:
    """Client for v30 Analytics endpoints (async)."""

    def __init__(self, api_call: AsyncApiCall) -> None:
        self.api_call = api_call
        self.rules = AsyncAnalyticsRules(api_call)
        self.events = AsyncAnalyticsEvents(api_call)
