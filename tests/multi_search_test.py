"""Tests for the MultiSearch class."""

import pytest

from tests.fixtures.document_fixtures import Companies
from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_keys,
)
from typesense import exceptions
from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.multi_search import AsyncMultiSearch
from typesense.sync.multi_search import MultiSearch
from typesense.types.multi_search import MultiSearchRequestSchema


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the MultiSearch object is initialized correctly."""
    multi_search = MultiSearch(fake_api_call)

    assert_match_object(multi_search.api_call, fake_api_call)
    assert_object_lists_match(
        multi_search.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        multi_search.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncMultiSearch object is initialized correctly."""
    multi_search = AsyncMultiSearch(fake_async_api_call)

    assert_match_object(multi_search.api_call, fake_async_api_call)
    assert_object_lists_match(
        multi_search.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        multi_search.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )


def test_multi_search_single_search(
    actual_multi_search: MultiSearch,
    actual_api_call: ApiCall,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the MultiSearch object can perform a single search."""
    request_params: MultiSearchRequestSchema = {
        "searches": [
            {"q": "com", "query_by": "company_name", "collection": "companies"},
        ],
    }
    response = actual_multi_search.perform(
        search_queries=request_params,
    )

    assert len(response.get("results")) == 1
    assert_to_contain_keys(
        response.get("results")[0],
        [
            "facet_counts",
            "found",
            "hits",
            "page",
            "out_of",
            "request_params",
            "search_time_ms",
            "search_cutoff",
        ],
    )

    assert_to_contain_keys(
        response.get("results")[0].get("hits")[0],
        ["document", "highlights", "highlight", "text_match", "text_match_info"],
    )


def test_multi_search_multiple_searches(
    actual_multi_search: MultiSearch,
    actual_api_call: ApiCall,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the MultiSearch object can perform multiple searches."""
    request_params: MultiSearchRequestSchema = {
        "searches": [
            {"q": "com", "query_by": "company_name", "collection": "companies"},
            {"q": "company", "query_by": "company_name", "collection": "companies"},
        ],
    }

    response = actual_multi_search.perform(search_queries=request_params)

    assert len(response.get("results")) == len(request_params.get("searches"))
    for search_results in response.get("results"):
        assert_to_contain_keys(
            search_results,
            [
                "facet_counts",
                "found",
                "hits",
                "page",
                "out_of",
                "request_params",
                "search_time_ms",
                "search_cutoff",
            ],
        )

        assert_to_contain_keys(
            search_results.get("hits")[0],
            ["document", "highlights", "highlight", "text_match", "text_match_info"],
        )


def test_multi_search_union(
    actual_multi_search: MultiSearch,
    actual_api_call: ApiCall,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the MultiSearch object can perform multiple searches."""
    request_params: MultiSearchRequestSchema = {
        "union": True,
        "searches": [
            {"q": "com", "query_by": "company_name", "collection": "companies"},
            {"q": "company", "query_by": "company_name", "collection": "companies"},
        ],
    }

    response = actual_multi_search.perform(search_queries=request_params)

    assert_to_contain_keys(
        response,
        [
            "found",
            "hits",
            "page",
            "out_of",
            "union_request_params",
            "search_time_ms",
            "search_cutoff",
        ],
    )

    assert_to_contain_keys(
        response.get("hits")[0],
        [
            "collection",
            "document",
            "highlights",
            "highlight",
            "text_match",
            "text_match_info",
            "search_index",
        ],
    )


def test_multi_search_array(
    actual_multi_search: MultiSearch,
    actual_api_call: ApiCall,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the MultiSearch object can perform a search with an array query_by."""
    request_params: MultiSearchRequestSchema = {
        "searches": [
            {"q": "com", "query_by": ["company_name"], "collection": "companies"},
        ],
    }
    response = actual_multi_search.perform(search_queries=request_params)

    assert len(response.get("results")) == 1
    assert_to_contain_keys(
        response.get("results")[0],
        [
            "facet_counts",
            "found",
            "hits",
            "page",
            "out_of",
            "request_params",
            "search_time_ms",
            "search_cutoff",
        ],
    )

    assert_to_contain_keys(
        response.get("results")[0].get("hits")[0],
        ["document", "highlights", "highlight", "text_match", "text_match_info"],
    )


def test_search_invalid_parameters(
    actual_multi_search: MultiSearch,
    actual_api_call: ApiCall,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the MultiSearch object raises an error when invalid parameters are passed."""
    with pytest.raises(exceptions.InvalidParameter):
        actual_multi_search.perform(
            {
                "searches": [
                    {
                        "q": "com",
                        "query_by": "company_name",
                        "invalid": [Companies(company_name="", id="", num_employees=0)],
                    },
                ],
            },
        )

    with pytest.raises(exceptions.InvalidParameter):
        actual_multi_search.perform(
            {
                "searches": [
                    {
                        "q": "com",
                        "query_by": "company_name",
                        "invalid": Companies(company_name="", id="", num_employees=0),
                    },
                ],
            },
        )


async def test_multi_search_single_search_async(
    actual_async_multi_search: AsyncMultiSearch,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the AsyncMultiSearch object can perform a single search."""
    request_params: MultiSearchRequestSchema = {
        "searches": [
            {"q": "com", "query_by": "company_name", "collection": "companies"},
        ],
    }
    response = await actual_async_multi_search.perform(
        search_queries=request_params,
    )

    assert len(response.get("results")) == 1
    assert_to_contain_keys(
        response.get("results")[0],
        [
            "facet_counts",
            "found",
            "hits",
            "page",
            "out_of",
            "request_params",
            "search_time_ms",
            "search_cutoff",
        ],
    )

    assert_to_contain_keys(
        response.get("results")[0].get("hits")[0],
        ["document", "highlights", "highlight", "text_match", "text_match_info"],
    )


async def test_multi_search_multiple_searches_async(
    actual_async_multi_search: AsyncMultiSearch,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the AsyncMultiSearch object can perform multiple searches."""
    request_params: MultiSearchRequestSchema = {
        "searches": [
            {"q": "com", "query_by": "company_name", "collection": "companies"},
            {"q": "company", "query_by": "company_name", "collection": "companies"},
        ],
    }

    response = await actual_async_multi_search.perform(search_queries=request_params)

    assert len(response.get("results")) == len(request_params.get("searches"))
    for search_results in response.get("results"):
        assert_to_contain_keys(
            search_results,
            [
                "facet_counts",
                "found",
                "hits",
                "page",
                "out_of",
                "request_params",
                "search_time_ms",
                "search_cutoff",
            ],
        )

        assert_to_contain_keys(
            search_results.get("hits")[0],
            ["document", "highlights", "highlight", "text_match", "text_match_info"],
        )


async def test_multi_search_union_async(
    actual_async_multi_search: AsyncMultiSearch,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the AsyncMultiSearch object can perform multiple searches with union."""
    request_params: MultiSearchRequestSchema = {
        "union": True,
        "searches": [
            {"q": "com", "query_by": "company_name", "collection": "companies"},
            {"q": "company", "query_by": "company_name", "collection": "companies"},
        ],
    }

    response = await actual_async_multi_search.perform(search_queries=request_params)

    assert_to_contain_keys(
        response,
        [
            "found",
            "hits",
            "page",
            "out_of",
            "union_request_params",
            "search_time_ms",
            "search_cutoff",
        ],
    )

    assert_to_contain_keys(
        response.get("hits")[0],
        [
            "collection",
            "document",
            "highlights",
            "highlight",
            "text_match",
            "text_match_info",
            "search_index",
        ],
    )


async def test_multi_search_array_async(
    actual_async_multi_search: AsyncMultiSearch,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the AsyncMultiSearch object can perform a search with an array query_by."""
    request_params: MultiSearchRequestSchema = {
        "searches": [
            {"q": "com", "query_by": ["company_name"], "collection": "companies"},
        ],
    }
    response = await actual_async_multi_search.perform(search_queries=request_params)

    assert len(response.get("results")) == 1
    assert_to_contain_keys(
        response.get("results")[0],
        [
            "facet_counts",
            "found",
            "hits",
            "page",
            "out_of",
            "request_params",
            "search_time_ms",
            "search_cutoff",
        ],
    )

    assert_to_contain_keys(
        response.get("results")[0].get("hits")[0],
        ["document", "highlights", "highlight", "text_match", "text_match_info"],
    )
