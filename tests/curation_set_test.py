"""Tests for the CurationSet class including items APIs."""

from __future__ import annotations

import pytest

from tests.utils.version import is_v30_or_above
from typesense.client import Client
from typesense.curation_set import CurationSet
from typesense.curation_sets import CurationSets
from typesense.types.curation_set import CurationItemSchema

pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run curation set tests only on v30+",
)


def test_paths(fake_curation_set: CurationSet) -> None:
    assert fake_curation_set._endpoint_path == "/curation_sets/products"  # noqa: WPS437
    assert fake_curation_set._items_path == "/curation_sets/products/items"  # noqa: WPS437


def test_actual_retrieve(
    actual_curation_sets: CurationSets,
    delete_all_curation_sets: None,
    create_curation_set: None,
) -> None:
    """Test that the CurationSet object can retrieve a curation set from Typesense Server."""
    response = actual_curation_sets["products"].retrieve()

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


def test_actual_delete(
    actual_curation_sets: CurationSets,
    create_curation_set: None,
) -> None:
    """Test that the CurationSet object can delete a curation set from Typesense Server."""
    response = actual_curation_sets["products"].delete()

    print(response)
    assert response == {"name": "products"}
