"""Tests for the Override class."""

from __future__ import annotations

import pytest

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.collections import Collections
from typesense.override import Override, OverrideDeleteSchema
from typesense.types.override import OverrideSchema
from tests.utils.version import is_v30_or_above
from typesense.client import Client


pytestmark = pytest.mark.skipif(
    is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run override tests only on less than v30",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Override object is initialized correctly."""
    override = Override(fake_api_call, "companies", "company_override")

    assert override.collection_name == "companies"
    assert override.override_id == "company_override"
    assert_match_object(override.api_call, fake_api_call)
    assert_object_lists_match(
        override.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        override.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert (
        override._endpoint_path()  # noqa: WPS437
        == "/collections/companies/overrides/company_override"
    )


def test_actual_retrieve(
    actual_collections: Collections,
    delete_all: None,
    create_override: None,
) -> None:
    """Test that the Override object can retrieve an override from Typesense Server."""
    response = actual_collections["companies"].overrides["company_override"].retrieve()

    assert response["rule"] == {
        "match": "exact",
        "query": "companies",
    }
    assert response["filter_by"] == "num_employees>10"
    assert_to_contain_object(
        response,
        {
            "rule": {
                "match": "exact",
                "query": "companies",
            },
            "filter_by": "num_employees>10",
        },
    )


def test_actual_delete(
    actual_collections: Collections,
    delete_all: None,
    create_override: None,
) -> None:
    """Test that the Override object can delete an override from Typesense Server."""
    response = actual_collections["companies"].overrides["company_override"].delete()

    assert response == {"id": "company_override"}
