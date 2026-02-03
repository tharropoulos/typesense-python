"""Tests for the ConversationsModels class."""


import os
import sys

import pytest

from tests.utils.object_assertions import (
    assert_match_object,
    assert_object_lists_match,
    assert_to_contain_keys,
    assert_to_contain_object,
)
from typesense.api_call import ApiCall
from typesense.async_api_call import AsyncApiCall
from typesense.async_conversations_models import AsyncConversationsModels
from typesense.conversations_models import ConversationsModels


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the ConversationsModels object is initialized correctly."""
    conversations_models = ConversationsModels(fake_api_call)

    assert_match_object(conversations_models.api_call, fake_api_call)
    assert_object_lists_match(
        conversations_models.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        conversations_models.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )

    assert not conversations_models.conversations_models


def test_init_async(fake_async_api_call: AsyncApiCall) -> None:
    """Test that the AsyncConversationsModels object is initialized correctly."""
    conversations_models = AsyncConversationsModels(fake_async_api_call)

    assert_match_object(conversations_models.api_call, fake_async_api_call)
    assert_object_lists_match(
        conversations_models.api_call.node_manager.nodes,
        fake_async_api_call.node_manager.nodes,
    )
    assert_match_object(
        conversations_models.api_call.config.nearest_node,
        fake_async_api_call.config.nearest_node,
    )

    assert not conversations_models.conversations_models


def test_get_missing_conversations_model(
    fake_conversations_models: ConversationsModels,
) -> None:
    """Test that the ConversationsModels object can get a missing conversations_model."""
    conversations_model = fake_conversations_models["conversation_model_id"]

    assert_match_object(
        conversations_model.api_call,
        fake_conversations_models.api_call,
    )
    assert_object_lists_match(
        conversations_model.api_call.node_manager.nodes,
        fake_conversations_models.api_call.node_manager.nodes,
    )
    assert_match_object(
        conversations_model.api_call.config.nearest_node,
        fake_conversations_models.api_call.config.nearest_node,
    )
    assert (
        conversations_model._endpoint_path  # noqa: WPS437
        == "/conversations/models/conversation_model_id"
    )


def test_get_missing_conversations_model_async(
    fake_async_conversations_models: AsyncConversationsModels,
) -> None:
    """Test that the AsyncConversationsModels object can get a missing conversations_model."""
    conversations_model = fake_async_conversations_models["conversation_model_id"]

    assert_match_object(
        conversations_model.api_call,
        fake_async_conversations_models.api_call,
    )
    assert_object_lists_match(
        conversations_model.api_call.node_manager.nodes,
        fake_async_conversations_models.api_call.node_manager.nodes,
    )
    assert_match_object(
        conversations_model.api_call.config.nearest_node,
        fake_async_conversations_models.api_call.config.nearest_node,
    )
    assert (
        conversations_model._endpoint_path  # noqa: WPS437
        == "/conversations/models/conversation_model_id"
    )


def test_get_existing_conversations_model(
    fake_conversations_models: ConversationsModels,
) -> None:
    """Test that the ConversationsModels object can get an existing conversations_model."""
    conversations_model = fake_conversations_models["conversations_model_id"]
    fetched_conversations_model = fake_conversations_models["conversations_model_id"]

    assert len(fake_conversations_models.conversations_models) == 1

    assert conversations_model is fetched_conversations_model


def test_get_existing_conversations_model_async(
    fake_async_conversations_models: AsyncConversationsModels,
) -> None:
    """Test that the AsyncConversationsModels object can get an existing conversations_model."""
    conversations_model = fake_async_conversations_models["conversations_model_id"]
    fetched_conversations_model = fake_async_conversations_models[
        "conversations_model_id"
    ]

    assert len(fake_async_conversations_models.conversations_models) == 1

    assert conversations_model is fetched_conversations_model


@pytest.mark.open_ai
def test_actual_create(
    actual_conversations_models: ConversationsModels,
    create_conversation_history_collection: None,
) -> None:
    """Test that it can create an conversations_model on Typesense Server."""
    response = actual_conversations_models.create(
        {
            "api_key": os.environ["OPEN_AI_KEY"],
            "history_collection": "conversation_store",
            "max_bytes": 16384,
            "model_name": "openai/gpt-3.5-turbo",
            "system_prompt": "This is meant for testing purposes",
        },
    )

    assert_to_contain_keys(
        response,
        ["id", "api_key", "max_bytes", "model_name", "system_prompt"],
    )


@pytest.mark.open_ai
def test_actual_retrieve(
    actual_conversations_models: ConversationsModels,
    delete_all: None,
    delete_all_conversations_models: None,
    create_conversations_model: str,
) -> None:
    """Test that it can retrieve an conversations_model from Typesense Server."""
    response = actual_conversations_models.retrieve()
    assert len(response) == 1
    assert_to_contain_object(
        response[0],
        {
            "id": create_conversations_model,
        },
    )
    assert_to_contain_keys(
        response[0],
        ["id", "api_key", "max_bytes", "model_name", "system_prompt"],
    )


@pytest.mark.open_ai
async def test_actual_create_async(
    actual_async_conversations_models: AsyncConversationsModels,
    create_conversation_history_collection: None,
) -> None:
    """Test that it can create an conversations_model on Typesense Server."""
    response = await actual_async_conversations_models.create(
        {
            "api_key": os.environ["OPEN_AI_KEY"],
            "history_collection": "conversation_store",
            "max_bytes": 16384,
            "model_name": "openai/gpt-3.5-turbo",
            "system_prompt": "This is meant for testing purposes",
        },
    )

    assert_to_contain_keys(
        response,
        ["id", "api_key", "max_bytes", "model_name", "system_prompt"],
    )


@pytest.mark.open_ai
async def test_actual_retrieve_async(
    actual_async_conversations_models: AsyncConversationsModels,
    delete_all: None,
    delete_all_conversations_models: None,
    create_conversations_model: str,
) -> None:
    """Test that it can retrieve an conversations_model from Typesense Server."""
    response = await actual_async_conversations_models.retrieve()
    assert len(response) == 1
    assert_to_contain_object(
        response[0],
        {
            "id": create_conversations_model,
        },
    )
    assert_to_contain_keys(
        response[0],
        ["id", "api_key", "max_bytes", "model_name", "system_prompt"],
    )
