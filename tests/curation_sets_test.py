"""Tests for the CurationSets class."""

from __future__ import annotations

import pytest

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from tests.utils.version import is_v30_or_above
from typesense.api_call import ApiCall
from typesense.client import Client
from typesense.curation_sets import CurationSets

pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run curation sets tests only on v30+",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the CurationSets object is initialized correctly."""
    cur_sets = CurationSets(fake_api_call)

    assert_match_object(cur_sets.api_call, fake_api_call)
    assert_object_lists_match(
        cur_sets.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )


def test_actual_upsert(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
) -> None:
    """Test that the CurationSets object can upsert a curation set on Typesense Server."""
    response = actual_curation_sets["products"].upsert(
        {
            "items": [
                {
                    "id": "rule-1",
                    "rule": {"query": "shoe", "match": "contains"},
                    "includes": [{"id": "123", "position": 1}],
                    "excludes": [{"id": "999"}],
                }
            ]
        },
    )

    assert response == {
        "items": [
            {
                "excludes": [
                    {
                        "id": "999",
                    },
                ],
                "filter_curated_hits": False,
                "id": "rule-1",
                "includes": [
                    {
                        "id": "123",
                        "position": 1,
                    },
                ],
                "remove_matched_tokens": False,
                "rule": {
                    "match": "contains",
                    "query": "shoe",
                },
                "stop_processing": True,
            },
        ],
        "name": "products",
    }


def test_actual_retrieve(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSets object can retrieve curation sets from Typesense Server."""
    response = actual_curation_sets.retrieve()

    assert isinstance(response, list)
    assert_to_contain_object(
        response[0],
        {
            "name": "products",
        },
    )
