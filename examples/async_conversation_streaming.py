import asyncio
import os
import sys

curr_dir = os.path.dirname(os.path.realpath(__file__))
repo_root = os.path.abspath(os.path.join(curr_dir, os.pardir))
sys.path.insert(1, os.path.join(repo_root, "src"))

import typesense

from typesense.types.document import MessageChunk, StreamConfigBuilder


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def main() -> None:
    typesense_api_key = require_env("TYPESENSE_API_KEY")
    openai_api_key = require_env("OPENAI_API_KEY")

    client = typesense.AsyncClient(
        {
            "api_key": typesense_api_key,
            "nodes": [
                {
                    "host": "localhost",
                    "port": "8108",
                    "protocol": "http",
                }
            ],
            "connection_timeout_seconds": 10,
        }
    )

    try:
        try:
            await client.conversations_models["conv-model-1"].delete()
        except Exception:
            pass

        try:
            await client.collections["streaming_docs"].delete()
        except Exception:
            pass

        try:
            await client.collections["conversation_store"].delete()
        except Exception:
            pass

        await client.collections.create(
            {
                "name": "conversation_store",
                "fields": [
                    {"name": "conversation_id", "type": "string"},
                    {"name": "model_id", "type": "string"},
                    {"name": "timestamp", "type": "int32"},
                    {"name": "role", "type": "string", "index": False},
                    {"name": "message", "type": "string", "index": False},
                ],
            }
        )

        await client.collections.create(
            {
                "name": "streaming_docs",
                "fields": [
                    {"name": "title", "type": "string"},
                    {
                        "name": "embedding",
                        "type": "float[]",
                        "embed": {
                            "from": ["title"],
                            "model_config": {
                                "model_name": "openai/text-embedding-3-small",
                                "api_key": openai_api_key,
                            },
                        },
                    },
                ],
            }
        )

        await client.collections["streaming_docs"].documents.create(
            {"id": "stream-1", "title": "Company profile: a developer tools firm."}
        )
        await client.collections["streaming_docs"].documents.create(
            {"id": "stream-2", "title": "Internal memo about quarterly planning."}
        )

        conversation_model = await client.conversations_models.create(
            {
                "id": "conv-model-1",
                "model_name": "openai/gpt-3.5-turbo",
                "history_collection": "conversation_store",
                "api_key": openai_api_key,
                "system_prompt": (
                    "You are an assistant for question-answering. "
                    "Only use the provided context. Add some fluff about you Being an assistant built for Typesense Conversational Search and a brief overview of how it works"
                ),
                "max_bytes": 16384,
            }
        )

        stream = StreamConfigBuilder()

        @stream.on_chunk
        def on_chunk(chunk: MessageChunk) -> None:
            print(chunk["message"], end="", flush=True)

        @stream.on_complete
        def on_complete(response: dict) -> None:
            print("\n---\nComplete response keys:", response.keys())

        await client.collections["streaming_docs"].documents.search(
            {
                "q": "What is this document about?",
                "query_by": "embedding",
                "exclude_fields": "embedding",
                "conversation": True,
                "prefix": False,
                "conversation_stream": True,
                "conversation_model_id": conversation_model["id"],
                "stream_config": stream,
            }
        )
    finally:
        await client.api_call.aclose()


if __name__ == "__main__":
    asyncio.run(main())
