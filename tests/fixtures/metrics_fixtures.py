"""Fixtures for the Metrics class tests."""

import pytest

from typesense.api_call import ApiCall
from typesense.async_api_call import AsyncApiCall
from typesense.async_metrics import AsyncMetrics
from typesense.metrics import Metrics


@pytest.fixture(scope="function", name="actual_metrics")
def actual_debug_fixture(actual_api_call: ApiCall) -> Metrics:
    """Return a Debug object using a real API."""
    return Metrics(actual_api_call)


@pytest.fixture(scope="function", name="actual_async_metrics")
def actual_async_metrics_fixture(actual_async_api_call: AsyncApiCall) -> AsyncMetrics:
    """Return a AsyncMetrics object using a real API."""
    return AsyncMetrics(actual_async_api_call)


@pytest.fixture(scope="function", name="fake_async_metrics")
def fake_async_metrics_fixture(fake_async_api_call: AsyncApiCall) -> AsyncMetrics:
    """Return a AsyncMetrics object with test values."""
    return AsyncMetrics(fake_async_api_call)
