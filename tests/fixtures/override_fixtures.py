"""Fixtures for the Overrides tests."""

import pytest
import requests

from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.override import AsyncOverride
from typesense.async_.overrides import AsyncOverrides
from typesense.sync.override import Override
from typesense.sync.overrides import Overrides


@pytest.fixture(scope="function", name="create_override")
def create_override_fixture(create_collection: None) -> None:
    """Create an override in the Typesense server."""
    url = "http://localhost:8108/collections/companies/overrides/company_override"
    headers = {"X-TYPESENSE-API-KEY": "xyz"}
    override_data = {
        "rule": {"match": "exact", "query": "companies"},
        "filter_by": "num_employees>10",
    }

    response = requests.put(url, headers=headers, json=override_data, timeout=3)
    response.raise_for_status()


@pytest.fixture(scope="function", name="actual_overrides")
def actual_overrides_fixture(actual_api_call: ApiCall) -> Overrides:
    """Return a Overrides object using a real API."""
    return Overrides(actual_api_call, "companies")


@pytest.fixture(scope="function", name="fake_overrides")
def fake_overrides_fixture(fake_api_call: ApiCall) -> Overrides:
    """Return a Override object with test values."""
    return Overrides(fake_api_call, "companies")


@pytest.fixture(scope="function", name="fake_override")
def fake_override_fixture(fake_api_call: ApiCall) -> Override:
    """Return a Override object with test values."""
    return Override(fake_api_call, "companies", "company_override")


@pytest.fixture(scope="function", name="actual_async_overrides")
def actual_async_overrides_fixture(
    actual_async_api_call: AsyncApiCall,
) -> AsyncOverrides:
    """Return a AsyncOverrides object using a real API."""
    return AsyncOverrides(actual_async_api_call, "companies")


@pytest.fixture(scope="function", name="fake_async_overrides")
def fake_async_overrides_fixture(
    fake_async_api_call: AsyncApiCall,
) -> AsyncOverrides:
    """Return a AsyncOverrides object with test values."""
    return AsyncOverrides(fake_async_api_call, "companies")


@pytest.fixture(scope="function", name="fake_async_override")
def fake_async_override_fixture(fake_async_api_call: AsyncApiCall) -> AsyncOverride:
    """Return a AsyncOverride object with test values."""
    return AsyncOverride(fake_async_api_call, "companies", "company_override")
