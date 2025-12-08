"""Tests for the Document class."""

from __future__ import annotations

import pytest

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.async_api_call import AsyncApiCall
from typesense.async_document import AsyncDocument
from typesense.async_documents import AsyncDocuments
from typesense.document import Document
from typesense.documents import Documents
from typesense.exceptions import ObjectNotFound


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Document object is initialized correctly."""
    document = Document(fake_api_call, "companies", "0")

    assert document.document_id == "0"
    assert document.collection_name == "companies"
    assert_match_object(document.api_call, fake_api_call)
    assert_object_lists_match(
        document.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        document.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert (
        document._endpoint_path == "/collections/companies/documents/0"  # noqa: WPS437
    )


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncDocument object is initialized correctly."""
    document = AsyncDocument(fake_async_api_call, "companies", "0")

    assert document.document_id == "0"
    assert document.collection_name == "companies"
    assert_match_object(document.api_call, fake_async_api_call)
    assert_object_lists_match(
        document.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        document.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )
    assert (
        document._endpoint_path == "/collections/companies/documents/0"  # noqa: WPS437
    )


def test_actual_update(
    actual_documents: Documents,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the Document object can update an document on Typesense Server."""
    response = actual_documents["0"].update(
        {"company_name": "Company", "num_employees": 20},
        {
            "action": "update",
        },
    )

    assert_to_contain_object(
        response,
        {"id": "0", "company_name": "Company", "num_employees": 20},
    )


def test_actual_retrieve(
    actual_documents: Documents,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the Document object can retrieve an document from Typesense Server."""
    response = actual_documents["0"].retrieve()

    assert_to_contain_object(
        response,
        {"id": "0", "company_name": "Company", "num_employees": 10},
    )


def test_actual_delete(
    actual_documents: Documents,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the Document object can delete an document from Typesense Server."""
    response = actual_documents["0"].delete()

    assert response == {
        "id": "0",
        "company_name": "Company",
        "num_employees": 10,
    }


def test_actual_delete_non_existent(
    actual_documents: Documents,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the Document object can delete an document from Typesense Server."""
    with pytest.raises(ObjectNotFound):
        actual_documents["1"].delete()


def test_actual_delete_non_existent_ignore_not_found(
    actual_documents: Documents,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the Document object can delete an document from Typesense Server."""
    response = actual_documents["1"].delete(
        delete_parameters={"ignore_not_found": True},
    )

    assert response == {"id": "1"}


async def test_actual_update_async(
    actual_async_documents: AsyncDocuments,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the AsyncDocument object can update an document on Typesense Server."""
    response = await actual_async_documents["0"].update(
        {"company_name": "Company", "num_employees": 20},
        {
            "action": "update",
        },
    )

    assert_to_contain_object(
        response,
        {"id": "0", "company_name": "Company", "num_employees": 20},
    )


async def test_actual_retrieve_async(
    actual_async_documents: AsyncDocuments,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the AsyncDocument object can retrieve an document from Typesense Server."""
    response = await actual_async_documents["0"].retrieve()

    assert_to_contain_object(
        response,
        {"id": "0", "company_name": "Company", "num_employees": 10},
    )


async def test_actual_delete_async(
    actual_async_documents: AsyncDocuments,
    delete_all: None,
    create_collection: None,
    create_document: None,
) -> None:
    """Test that the AsyncDocument object can delete an document from Typesense Server."""
    response = await actual_async_documents["0"].delete()

    assert response == {
        "id": "0",
        "company_name": "Company",
        "num_employees": 10,
    }
