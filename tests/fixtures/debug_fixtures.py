"""Fixtures for the Debug class tests."""

import pytest

from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.debug import AsyncDebug
from typesense.sync.debug import Debug


@pytest.fixture(scope="function", name="actual_debug")
def actual_debug_fixture(actual_api_call: ApiCall) -> Debug:
    """Return a Debug object using a real API."""
    return Debug(actual_api_call)


@pytest.fixture(scope="function", name="fake_debug")
def fake_debug_fixture(fake_api_call: ApiCall) -> Debug:
    """Return a debug object with test values."""
    return Debug(fake_api_call)


@pytest.fixture(scope="function", name="actual_async_debug")
def actual_async_debug_fixture(actual_async_api_call: AsyncApiCall) -> AsyncDebug:
    """Return a AsyncDebug object using a real API."""
    return AsyncDebug(actual_async_api_call)


@pytest.fixture(scope="function", name="fake_async_debug")
def fake_async_debug_fixture(fake_async_api_call: AsyncApiCall) -> AsyncDebug:
    """Return a AsyncDebug object with test values."""
    return AsyncDebug(fake_async_api_call)
