"""Tests for the Stopwords class."""

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.async_api_call import AsyncApiCall
from typesense.async_stopwords import AsyncStopwords
from typesense.stopwords import Stopwords
from typesense.types.stopword import StopwordSchema, StopwordsRetrieveSchema


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Stopwords object is initialized correctly."""
    stopwords = Stopwords(fake_api_call)

    assert_match_object(stopwords.api_call, fake_api_call)
    assert_object_lists_match(
        stopwords.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        stopwords.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not stopwords.stopwords_sets


def test_get_missing_stopword(fake_stopwords: Stopwords) -> None:
    """Test that the Stopwords object can get a missing stopword."""
    stopword = fake_stopwords["company_stopwords"]

    assert stopword.stopwords_set_id == "company_stopwords"
    assert_match_object(stopword.api_call, fake_stopwords.api_call)
    assert_object_lists_match(
        stopword.api_call.node_manager.nodes, fake_stopwords.api_call.node_manager.nodes
    )
    assert_match_object(
        stopword.api_call.config.nearest_node,
        fake_stopwords.api_call.config.nearest_node,
    )
    assert stopword._endpoint_path == "/stopwords/company_stopwords"  # noqa: WPS437


def test_get_existing_stopword(fake_stopwords: Stopwords) -> None:
    """Test that the Stopwords object can get an existing stopword."""
    stopword = fake_stopwords["company_stopwords"]
    fetched_stopword = fake_stopwords["company_stopwords"]

    assert len(fake_stopwords.stopwords_sets) == 1

    assert stopword is fetched_stopword


def test_actual_create(actual_stopwords: Stopwords, delete_all_stopwords: None) -> None:
    """Test that the Stopwords object can create an stopword on Typesense Server."""
    response = actual_stopwords.upsert(
        "company_stopwords",
        {"stopwords": ["and", "is", "the"]},
    )

    assert response == {
        "id": "company_stopwords",
        "stopwords": ["and", "is", "the"],
    }


def test_actual_update(
    actual_stopwords: Stopwords,
    delete_all_stopwords: None,
) -> None:
    """Test that the Stopwords object can update an stopword on Typesense Server."""
    create_response = actual_stopwords.upsert(
        "company_stopwords",
        {"stopwords": ["and", "is", "the"]},
    )

    assert create_response == {
        "id": "company_stopwords",
        "stopwords": ["and", "is", "the"],
    }

    update_response = actual_stopwords.upsert(
        "company_stopwords",
        {"stopwords": ["and", "is", "other"]},
    )

    assert update_response == {
        "id": "company_stopwords",
        "stopwords": ["and", "is", "other"],
    }


def test_actual_retrieve(
    delete_all_stopwords: None,
    create_stopword: None,
    actual_stopwords: Stopwords,
) -> None:
    """Test that the Stopwords object can retrieve an stopword from Typesense Server."""
    response = actual_stopwords.retrieve()

    assert len(response["stopwords"]) == 1
    assert_to_contain_object(
        response["stopwords"][0],
        {
            "id": "company_stopwords",
            "stopwords": ["and", "is", "the"],
        },
    )


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncStopwords object is initialized correctly."""
    stopwords = AsyncStopwords(fake_async_api_call)

    assert_match_object(stopwords.api_call, fake_async_api_call)
    assert_object_lists_match(
        stopwords.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        stopwords.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )

    assert not stopwords.stopwords_sets


def test_get_missing_stopword_async(fake_async_stopwords: AsyncStopwords) -> None:
    """Test that the AsyncStopwords object can get a missing stopword."""
    stopword = fake_async_stopwords["company_stopwords"]

    assert stopword.stopwords_set_id == "company_stopwords"
    assert_match_object(stopword.api_call, fake_async_stopwords.api_call)
    assert_object_lists_match(
        stopword.api_call.node_manager.nodes, fake_async_stopwords.api_call.node_manager.nodes
    )
    assert_match_object(
        stopword.api_call.config.nearest_node,
        fake_async_stopwords.api_call.config.nearest_node,
    )
    assert stopword._endpoint_path == "/stopwords/company_stopwords"  # noqa: WPS437


def test_get_existing_stopword_async(fake_async_stopwords: AsyncStopwords) -> None:
    """Test that the AsyncStopwords object can get an existing stopword."""
    stopword = fake_async_stopwords["company_stopwords"]
    fetched_stopword = fake_async_stopwords["company_stopwords"]

    assert len(fake_async_stopwords.stopwords_sets) == 1

    assert stopword is fetched_stopword


async def test_actual_create_async(actual_async_stopwords: AsyncStopwords, delete_all_stopwords: None) -> None:
    """Test that the AsyncStopwords object can create an stopword on Typesense Server."""
    response = await actual_async_stopwords.upsert(
        "company_stopwords",
        {"stopwords": ["and", "is", "the"]},
    )

    assert response == {
        "id": "company_stopwords",
        "stopwords": ["and", "is", "the"],
    }


async def test_actual_update_async(
    actual_async_stopwords: AsyncStopwords,
    delete_all_stopwords: None,
) -> None:
    """Test that the AsyncStopwords object can update an stopword on Typesense Server."""
    create_response = await actual_async_stopwords.upsert(
        "company_stopwords",
        {"stopwords": ["and", "is", "the"]},
    )

    assert create_response == {
        "id": "company_stopwords",
        "stopwords": ["and", "is", "the"],
    }

    update_response = await actual_async_stopwords.upsert(
        "company_stopwords",
        {"stopwords": ["and", "is", "other"]},
    )

    assert update_response == {
        "id": "company_stopwords",
        "stopwords": ["and", "is", "other"],
    }


async def test_actual_retrieve_async(
    delete_all_stopwords: None,
    create_stopword: None,
    actual_async_stopwords: AsyncStopwords,
) -> None:
    """Test that the AsyncStopwords object can retrieve an stopword from Typesense Server."""
    response = await actual_async_stopwords.retrieve()

    assert len(response["stopwords"]) == 1
    assert_to_contain_object(
        response["stopwords"][0],
        {
            "id": "company_stopwords",
            "stopwords": ["and", "is", "the"],
        },
    )
