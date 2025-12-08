"""Tests for the Keys class."""


import base64
import hashlib
import hmac
import json


from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.async_api_call import AsyncApiCall
from typesense.async_keys import AsyncKeys
from typesense.keys import Keys


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Keys object is initialized correctly."""
    keys = Keys(fake_api_call)

    assert_match_object(keys.api_call, fake_api_call)
    assert_object_lists_match(
        keys.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        keys.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not keys.keys


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncKeys object is initialized correctly."""
    keys = AsyncKeys(fake_async_api_call)

    assert_match_object(keys.api_call, fake_async_api_call)
    assert_object_lists_match(
        keys.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        keys.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )

    assert not keys.keys


def test_get_missing_key(fake_keys: Keys) -> None:
    """Test that the Keys object can get a missing key."""
    key = fake_keys[1]

    assert_match_object(key.api_call, fake_keys.api_call)
    assert_object_lists_match(
        key.api_call.node_manager.nodes, fake_keys.api_call.node_manager.nodes
    )
    assert_match_object(
        key.api_call.config.nearest_node,
        fake_keys.api_call.config.nearest_node,
    )
    assert key._endpoint_path == "/keys/1"  # noqa: WPS437


def test_get_missing_key_async(fake_async_keys: AsyncKeys) -> None:
    """Test that the AsyncKeys object can get a missing key."""
    key = fake_async_keys[1]

    assert_match_object(key.api_call, fake_async_keys.api_call)
    assert_object_lists_match(
        key.api_call.node_manager.nodes,
        fake_async_keys.api_call.node_manager.nodes,
    )
    assert_match_object(
        key.api_call.config.nearest_node,
        fake_async_keys.api_call.config.nearest_node,
    )
    assert key._endpoint_path == "/keys/1"  # noqa: WPS437


def test_get_existing_key(fake_keys: Keys) -> None:
    """Test that the Keys object can get an existing key."""
    key = fake_keys[1]
    fetched_key = fake_keys[1]

    assert len(fake_keys.keys) == 1

    assert key is fetched_key


def test_get_existing_key_async(fake_async_keys: AsyncKeys) -> None:
    """Test that the AsyncKeys object can get an existing key."""
    key = fake_async_keys[1]
    fetched_key = fake_async_keys[1]

    assert len(fake_async_keys.keys) == 1

    assert key is fetched_key


def test_actual_create(
    actual_keys: Keys,
) -> None:
    """Test that the Keys object can create an key on Typesense Server."""
    response = actual_keys.create(
        {
            "actions": ["documents:search"],
            "collections": ["companies"],
            "description": "Search-only key",
        },
    )

    assert_to_contain_object(
        response,
        {
            "actions": ["documents:search"],
            "collections": ["companies"],
            "description": "Search-only key",
            "autodelete": False,
        },
    )


def test_actual_retrieve(
    actual_keys: Keys,
    delete_all: None,
    delete_all_keys: None,
    create_key_id: int,
) -> None:
    """Test that the Keys object can retrieve an key from Typesense Server."""
    response = actual_keys.retrieve()
    assert len(response["keys"]) == 1
    assert_to_contain_object(
        response["keys"][0],
        {
            "actions": ["documents:search"],
            "collections": ["companies"],
            "description": "Search-only key",
            "autodelete": False,
            "id": create_key_id,
        },
    )


def test_generate_scoped_search_key(
    fake_keys: Keys,
) -> None:
    """Test that the Keys object can generate a scoped search key."""
    # Use a real key that works on Typesense server
    search_key = "KmacipDKNqAM3YiigXfw5pZvNOrPQUba"
    search_parameters = {
        "q": "search query",
        "collection": "companies",
        "filter_by": "num_employees:>10",
    }

    key = fake_keys.generate_scoped_search_key(search_key, search_parameters)

    decoded_key = base64.b64decode(key).decode("utf-8")

    extracted_key = {
        "digest": decoded_key[:44],
        "key_prefix": decoded_key[44:48],
        "params_str": decoded_key[48:],
    }
    assert extracted_key["key_prefix"] == search_key[:4]

    expected_params_str = json.dumps(search_parameters)
    assert extracted_key["params_str"] == expected_params_str

    recomputed_digest = base64.b64encode(
        hmac.new(
            search_key.encode("utf-8"),
            expected_params_str.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest(),
    ).decode("utf-8")

    assert extracted_key["digest"] == recomputed_digest


async def test_actual_create_async(
    actual_async_keys: AsyncKeys,
) -> None:
    """Test that the AsyncKeys object can create an key on Typesense Server."""
    response = await actual_async_keys.create(
        {
            "actions": ["documents:search"],
            "collections": ["companies"],
            "description": "Search-only key",
        },
    )

    assert_to_contain_object(
        response,
        {
            "actions": ["documents:search"],
            "collections": ["companies"],
            "description": "Search-only key",
            "autodelete": False,
        },
    )


async def test_actual_retrieve_async(
    actual_async_keys: AsyncKeys,
    delete_all: None,
    delete_all_keys: None,
    create_key_id: int,
) -> None:
    """Test that the AsyncKeys object can retrieve an key from Typesense Server."""
    response = await actual_async_keys.retrieve()
    assert len(response["keys"]) == 1
    assert_to_contain_object(
        response["keys"][0],
        {
            "actions": ["documents:search"],
            "collections": ["companies"],
            "description": "Search-only key",
            "autodelete": False,
            "id": create_key_id,
        },
    )


def test_generate_scoped_search_key_async(
    fake_async_keys: AsyncKeys,
) -> None:
    """Test that the AsyncKeys object can generate a scoped search key."""
    # Use a real key that works on Typesense server
    search_key = "KmacipDKNqAM3YiigXfw5pZvNOrPQUba"
    search_parameters = {
        "q": "search query",
        "collection": "companies",
        "filter_by": "num_employees:>10",
    }

    key = fake_async_keys.generate_scoped_search_key(search_key, search_parameters)

    decoded_key = base64.b64decode(key).decode("utf-8")

    extracted_key = {
        "digest": decoded_key[:44],
        "key_prefix": decoded_key[44:48],
        "params_str": decoded_key[48:],
    }
    assert extracted_key["key_prefix"] == search_key[:4]

    expected_params_str = json.dumps(search_parameters)
    assert extracted_key["params_str"] == expected_params_str

    recomputed_digest = base64.b64encode(
        hmac.new(
            search_key.encode("utf-8"),
            expected_params_str.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest(),
    ).decode("utf-8")

    assert extracted_key["digest"] == recomputed_digest
