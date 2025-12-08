"""Tests for the SynonymSet class."""


import pytest

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from tests.utils.version import is_v30_or_above
from typesense.api_call import ApiCall
from typesense.async_api_call import AsyncApiCall
from typesense.async_synonym_sets import AsyncSynonymSets
from typesense.client import Client
from typesense.synonym_set import SynonymSet
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
    reason="Run synonym set tests only on v30+",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the SynonymSet object is initialized correctly."""
    synset = SynonymSet(fake_api_call, "test-set")

    assert synset.name == "test-set"
    assert_match_object(synset.api_call, fake_api_call)
    assert_object_lists_match(
        synset.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        synset.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert synset._endpoint_path == "/synonym_sets/test-set"  # noqa: WPS437


def test_actual_retrieve(
    actual_synonym_sets: SynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSet object can retrieve a synonym set from Typesense Server."""
    response = actual_synonym_sets["test-set"].retrieve()

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


def test_actual_delete(
    actual_synonym_sets: SynonymSets,
    create_synonym_set: None,
) -> None:
    """Test that the SynonymSet object can delete a synonym set from Typesense Server."""
    response = actual_synonym_sets["test-set"].delete()

    assert response == {"name": "test-set"}


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncSynonymSet object is initialized correctly."""
    from typesense.async_synonym_set import AsyncSynonymSet

    synset = AsyncSynonymSet(fake_async_api_call, "test-set")

    assert synset.name == "test-set"
    assert_match_object(synset.api_call, fake_async_api_call)
    assert_object_lists_match(
        synset.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        synset.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )
    assert synset._endpoint_path == "/synonym_sets/test-set"  # noqa: WPS437


async def test_actual_retrieve_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    delete_all_synonym_sets: None,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSet object can retrieve a synonym set from Typesense Server."""
    response = await actual_async_synonym_sets["test-set"].retrieve()

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


async def test_actual_delete_async(
    actual_async_synonym_sets: AsyncSynonymSets,
    create_synonym_set: None,
) -> None:
    """Test that the AsyncSynonymSet object can delete a synonym set from Typesense Server."""
    response = await actual_async_synonym_sets["test-set"].delete()

    assert response == {"name": "test-set"}
