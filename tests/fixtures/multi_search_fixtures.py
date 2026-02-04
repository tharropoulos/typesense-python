"""Fixtures for the MultiSearch class."""

import pytest

from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.multi_search import AsyncMultiSearch
from typesense.sync.multi_search import MultiSearch


@pytest.fixture(scope="function", name="actual_multi_search")
def actual_multi_search_fixture(actual_api_call: ApiCall) -> MultiSearch:
    """Return a MultiSearch object using a real API."""
    return MultiSearch(actual_api_call)


@pytest.fixture(scope="function", name="actual_async_multi_search")
def actual_async_multi_search_fixture(
    actual_async_api_call: AsyncApiCall,
) -> AsyncMultiSearch:
    """Return a AsyncMultiSearch object using a real API."""
    return AsyncMultiSearch(actual_async_api_call)


@pytest.fixture(scope="function", name="fake_async_multi_search")
def fake_async_multi_search_fixture(
    fake_async_api_call: AsyncApiCall,
) -> AsyncMultiSearch:
    """Return a AsyncMultiSearch object with test values."""
    return AsyncMultiSearch(fake_async_api_call)
