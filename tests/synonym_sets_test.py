"""Tests for the SynonymSets class."""

import pytest

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from tests.utils.version import is_v30_or_above
from typesense.api_call import ApiCall
from typesense.async_api_call import AsyncApiCall
from typesense.async_synonym_sets import AsyncSynonymSets
from typesense.client import Client
from typesense.synonym_sets import SynonymSets

pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run synonym sets tests only on v30+",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the SynonymSets object is initialized correctly."""
    synsets = SynonymSets(fake_api_call)

    assert_match_object(synsets.api_call, fake_api_call)
    assert_object_lists_match(
        synsets.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        synsets.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )


def test_actual_create(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
) -> None:
    """Test that the SynonymSets object can create a synonym set on Typesense Server."""
    response = actual_synonym_sets["test-set"].upsert(
        {
            "items": [
                {
                    "id": "company_synonym",
                    "synonyms": ["companies", "corporations", "firms"],
                }
            ]
        },
    )

    assert response == {
        "name": "test-set",
        "items": [
            {
                "id": "company_synonym",
                "root": "",
                "synonyms": ["companies", "corporations", "firms"],
            }
        ],
    }


def test_actual_retrieve(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSets object can retrieve a synonym set from Typesense Server."""
    response = actual_synonym_sets.retrieve()

    assert isinstance(response, list)
    assert_to_contain_object(
        response[0],
        {
            "name": "test-set",
        },
    )


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncSynonymSets object is initialized correctly."""
    from typesense.async_synonym_sets import AsyncSynonymSets

    synsets = AsyncSynonymSets(fake_async_api_call)

    assert_match_object(synsets.api_call, fake_async_api_call)
    assert_object_lists_match(
        synsets.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        synsets.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )


async def test_actual_create_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
) -> None:
    """Test that the AsyncSynonymSets object can create a synonym set on Typesense Server."""
    response = await actual_async_synonym_sets["test-set"].upsert(
        {
            "items": [
                {
                    "id": "company_synonym",
                    "synonyms": ["companies", "corporations", "firms"],
                }
            ]
        },
    )

    assert response == {
        "name": "test-set",
        "items": [
            {
                "id": "company_synonym",
                "root": "",
                "synonyms": ["companies", "corporations", "firms"],
            }
        ],
    }


async def test_actual_retrieve_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSets object can retrieve a synonym set from Typesense Server."""
    response = await actual_async_synonym_sets.retrieve()

    assert isinstance(response, list)
    assert_to_contain_object(
        response[0],
        {
            "name": "test-set",
        },
    )
