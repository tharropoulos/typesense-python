"""Tests for SynonymSet item-level APIs."""

from __future__ import annotations

import pytest

from tests.utils.version import is_v30_or_above
from typesense.client import Client
from typesense.synonym_sets import SynonymSets
from typesense.types.synonym_set import (
    SynonymItemSchema,
)

pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run synonym set items tests only on v30+",
)


def test_actual_list_items(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSet object can list items from Typesense Server."""
    response = actual_synonym_sets["test-set"].list_items()

    assert response == [
        {
            "id": "company_synonym",
            "root": "",
            "synonyms": ["companies", "corporations", "firms"],
        },
    ]


def test_actual_get_item(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSet object can get a specific item from Typesense Server."""
    response = actual_synonym_sets["test-set"].get_item("company_synonym")

    assert response == {
        "id": "company_synonym",
        "root": "",
        "synonyms": ["companies", "corporations", "firms"],
    }


def test_actual_upsert_item(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSet object can upsert an item in Typesense Server."""
    payload: SynonymItemSchema = {
        "id": "brand_synonym",
        "synonyms": ["brand", "brands", "label"],
    }
    response = actual_synonym_sets["test-set"].upsert_item("brand_synonym", payload)

    assert response == {
        "id": "brand_synonym",
        "synonyms": ["brand", "brands", "label"],
    }


def test_actual_delete_item(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSet object can delete an item from Typesense Server."""
    response = actual_synonym_sets["test-set"].delete_item("company_synonym")

    assert response == {"id": "company_synonym"}
