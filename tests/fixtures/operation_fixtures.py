"""Fixtures for the Operations tests."""

import pytest

from typesense.api_call import ApiCall
from typesense.async_api_call import AsyncApiCall
from typesense.async_operations import AsyncOperations
from typesense.operations import Operations


@pytest.fixture(scope="function", name="actual_operations")
def actual_operations_fixture(actual_api_call: ApiCall) -> Operations:
    """Return a Operations object using a real API."""
    return Operations(actual_api_call)


@pytest.fixture(scope="function", name="fake_operations")
def fake_operations_fixture(fake_api_call: ApiCall) -> Operations:
    """Return a Collection object with test values."""
    return Operations(fake_api_call)


@pytest.fixture(scope="function", name="actual_async_operations")
def actual_async_operations_fixture(
    actual_async_api_call: AsyncApiCall,
) -> AsyncOperations:
    """Return a AsyncOperations object using a real API."""
    return AsyncOperations(actual_async_api_call)


@pytest.fixture(scope="function", name="fake_async_operations")
def fake_async_operations_fixture(
    fake_async_api_call: AsyncApiCall,
) -> AsyncOperations:
    """Return a AsyncOperations object with test values."""
    return AsyncOperations(fake_async_api_call)
