"""Tests for the StopwordsSet class."""

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.api_call import ApiCall
from typesense.async_api_call import AsyncApiCall
from typesense.async_stopwords import AsyncStopwords
from typesense.stopwords import Stopwords
from typesense.stopwords_set import StopwordsSet


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the StopwordsSet object is initialized correctly."""
    stopword_set = StopwordsSet(fake_api_call, "company_stopwords")

    assert stopword_set.stopwords_set_id == "company_stopwords"
    assert_match_object(stopword_set.api_call, fake_api_call)
    assert_object_lists_match(
        stopword_set.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        stopword_set.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert stopword_set._endpoint_path == "/stopwords/company_stopwords"  # noqa: WPS437


def test_actual_retrieve(
    actual_stopwords: Stopwords,
    delete_all_stopwords: None,
    delete_all: None,
    create_stopword: None,
) -> None:
    """Test that the StopwordsSet object can retrieve an stopword_set from Typesense Server."""
    response = actual_stopwords["company_stopwords"].retrieve()

    assert response == {
        "stopwords": {
            "id": "company_stopwords",
            "stopwords": ["and", "is", "the"],
        },
    }


def test_actual_delete(
    actual_stopwords: Stopwords,
    create_stopword: None,
) -> None:
    """Test that the StopwordsSet object can delete an stopword_set from Typesense Server."""
    response = actual_stopwords["company_stopwords"].delete()

    assert response == {"id": "company_stopwords"}


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncStopwordsSet object is initialized correctly."""
    from typesense.async_stopwords_set import AsyncStopwordsSet

    stopword_set = AsyncStopwordsSet(fake_async_api_call, "company_stopwords")

    assert stopword_set.stopwords_set_id == "company_stopwords"
    assert_match_object(stopword_set.api_call, fake_async_api_call)
    assert_object_lists_match(
        stopword_set.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        stopword_set.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )
    assert stopword_set._endpoint_path == "/stopwords/company_stopwords"  # noqa: WPS437


async def test_actual_retrieve_async(
    actual_async_stopwords: AsyncStopwords,
    delete_all_stopwords: None,
    delete_all: None,
    create_stopword: None,
) -> None:
    """Test that the AsyncStopwordsSet object can retrieve an stopword_set from Typesense Server."""
    response = await actual_async_stopwords["company_stopwords"].retrieve()

    assert response == {
        "stopwords": {
            "id": "company_stopwords",
            "stopwords": ["and", "is", "the"],
        },
    }


async def test_actual_delete_async(
    actual_async_stopwords: AsyncStopwords,
    create_stopword: None,
) -> None:
    """Test that the AsyncStopwordsSet object can delete an stopword_set from Typesense Server."""
    response = await actual_async_stopwords["company_stopwords"].delete()

    assert response == {"id": "company_stopwords"}
