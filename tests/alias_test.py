"""Tests for the Alias class."""

from __future__ import annotations
from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.alias import Alias
from typesense.aliases import Aliases
from typesense.api_call import ApiCall


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Alias object is initialized correctly."""
    alias = Alias(fake_api_call, "company_alias")

    assert alias.name == "company_alias"
    assert_match_object(alias.api_call, fake_api_call)
    assert_object_lists_match(
        alias.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        alias.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert alias._endpoint_path == "/aliases/company_alias"  # noqa: WPS437


def test_actual_retrieve(
    actual_aliases: Aliases,
    delete_all_aliases: None,
    delete_all: None,
    create_alias: None,
) -> None:
    """Test that the Alias object can retrieve an alias from Typesense Server."""
    response = actual_aliases["company_alias"].retrieve()

    assert response["collection_name"] == "companies"
    assert response["name"] == "company_alias"

    assert_to_contain_object(
        response,
        {
            "collection_name": "companies",
            "name": "company_alias",
        },
    )


def test_actual_delete(
    actual_aliases: Aliases,
    delete_all_aliases: None,
    delete_all: None,
    create_alias: None,
) -> None:
    """Test that the Alias object can delete an alias from Typesense Server."""
    response = actual_aliases["company_alias"].delete()

    assert response == {
        "collection_name": "companies",
        "name": "company_alias",
    }
