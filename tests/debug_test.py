"""Tests for the Debug class."""

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from typesense.sync.api_call import ApiCall
from typesense.async_.api_call import AsyncApiCall
from typesense.async_.debug import AsyncDebug
from typesense.sync.debug import Debug


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the Debug object is initialized correctly."""
    debug = Debug(
        fake_api_call,
    )

    assert_match_object(debug.api_call, fake_api_call)
    assert_object_lists_match(
        debug.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        debug.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert debug.resource_path == "/debug"  # noqa: WPS437


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncDebug object is initialized correctly."""
    debug = AsyncDebug(fake_async_api_call)

    assert_match_object(debug.api_call, fake_async_api_call)
    assert_object_lists_match(
        debug.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        debug.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )
    assert debug.resource_path == "/debug"  # noqa: WPS437


def test_actual_retrieve(actual_debug: Debug) -> None:
    """Test that the Debug object can retrieve a debug on Typesense server and verify response structure."""
    response = actual_debug.retrieve()

    assert "state" in response
    assert "version" in response

    assert isinstance(response["state"], int)
    assert isinstance(response["version"], str)


async def test_actual_retrieve_async(actual_async_debug: AsyncDebug) -> None:
    """Test that the AsyncDebug object can retrieve a debug on Typesense server and verify response structure."""
    response = await actual_async_debug.retrieve()

    assert "state" in response
    assert "version" in response

    assert isinstance(response["state"], int)
    assert isinstance(response["version"], str)
