"""Fixtures for the Analytics Rules tests."""

import pytest

from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.stemming import AsyncStemming
from typesense.sync.stemming import Stemming


@pytest.fixture(scope="function", name="actual_stemming")
def actual_stemming_fixture(
    actual_api_call: ApiCall,
) -> Stemming:
    """Return a Stemming object using a real API."""
    return Stemming(actual_api_call)


@pytest.fixture(scope="function", name="actual_async_stemming")
def actual_async_stemming_fixture(
    actual_async_api_call: AsyncApiCall,
) -> AsyncStemming:
    """Return a AsyncStemming object using a real API."""
    return AsyncStemming(actual_async_api_call)


@pytest.fixture(scope="function", name="fake_async_stemming")
def fake_async_stemming_fixture(
    fake_async_api_call: AsyncApiCall,
) -> AsyncStemming:
    """Return a AsyncStemming object with test values."""
    return AsyncStemming(fake_async_api_call)
