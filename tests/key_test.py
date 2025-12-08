"""Tests for the Key class."""



from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.async_api_call import AsyncApiCall
from typesense.async_key import AsyncKey
from typesense.async_keys import AsyncKeys
from typesense.key import Key
from typesense.keys import Keys


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Key object is initialized correctly."""
    key = Key(fake_api_call, 3)

    assert key.key_id == 3
    assert_match_object(key.api_call, fake_api_call)
    assert_object_lists_match(
        key.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        key.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert key._endpoint_path == "/keys/3"  # noqa: WPS437


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncKey object is initialized correctly."""
    key = AsyncKey(fake_async_api_call, 3)

    assert key.key_id == 3
    assert_match_object(key.api_call, fake_async_api_call)
    assert_object_lists_match(
        key.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        key.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )
    assert key._endpoint_path == "/keys/3"  # noqa: WPS437


def test_actual_retrieve(
    actual_keys: Keys,
    delete_all_keys: None,
    delete_all: None,
    create_key_id: int,
) -> None:
    """Test that the Key object can retrieve an key from Typesense Server."""
    response = actual_keys[create_key_id].retrieve()

    assert_to_contain_object(
        response,
        {
            "actions": ["documents:search"],
            "collections": ["companies"],
            "description": "Search-only key",
            "id": create_key_id,
        },
    )


def test_actual_delete(
    actual_keys: Keys,
    delete_all_keys: None,
    delete_all: None,
    create_key_id: int,
) -> None:
    """Test that the Key object can delete an key from Typesense Server."""
    response = actual_keys[create_key_id].delete()

    assert response == {"id": create_key_id}


async def test_actual_retrieve_async(
    actual_async_keys: AsyncKeys,
    delete_all_keys: None,
    delete_all: None,
    create_key_id: int,
) -> None:
    """Test that the AsyncKey object can retrieve an key from Typesense Server."""
    response = await actual_async_keys[create_key_id].retrieve()

    assert_to_contain_object(
        response,
        {
            "actions": ["documents:search"],
            "collections": ["companies"],
            "description": "Search-only key",
            "id": create_key_id,
        },
    )


async def test_actual_delete_async(
    actual_async_keys: AsyncKeys,
    delete_all_keys: None,
    delete_all: None,
    create_key_id: int,
) -> None:
    """Test that the AsyncKey object can delete an key from Typesense Server."""
    response = await actual_async_keys[create_key_id].delete()

    assert response == {"id": create_key_id}
