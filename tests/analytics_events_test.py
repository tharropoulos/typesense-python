"""Tests for Analytics events endpoints (client.analytics.events)."""

import pytest

from tests.utils.version import is_v30_or_above
from typesense.async_analytics_events import AsyncAnalyticsEvents
from typesense.async_analytics_rules import AsyncAnalyticsRules
from typesense.client import Client
from typesense.types.analytics import AnalyticsEvent

pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run analytics events tests only on v30+",
)


def test_actual_create_event(
    actual_client: Client,
    delete_all: None,
    create_collection: None,
    delete_all_analytics_rules: None,
) -> None:
    actual_client.analytics.rules.create(
        {
            "name": "company_analytics_rule",
            "type": "log",
            "collection": "companies",
            "event_type": "click",
            "params": {},
        }
    )
    event: AnalyticsEvent = {
        "name": "company_analytics_rule",
        "event_type": "query",
        "data": {
            "user_id": "user-1",
            "doc_id": "apple",
        },
    }
    resp = actual_client.analytics.events.create(event)
    assert resp["ok"] is True
    actual_client.analytics.rules["company_analytics_rule"].delete()


def test_status(actual_client: Client, delete_all: None) -> None:
    status = actual_client.analytics.events.status()
    assert isinstance(status, dict)


def test_retrieve_events(
    actual_client: Client, delete_all: None, delete_all_analytics_rules: None
) -> None:
    actual_client.collections.create(
        {
            "name": "companies",
            "fields": [
                {"name": "user_id", "type": "string"},
            ],
        }
    )

    actual_client.analytics.rules.create(
        {
            "name": "company_analytics_rule",
            "type": "log",
            "collection": "companies",
            "event_type": "click",
            "params": {},
        }
    )
    event: AnalyticsEvent = {
        "name": "company_analytics_rule",
        "event_type": "query",
        "data": {
            "user_id": "user-1",
            "doc_id": "apple",
        },
    }
    resp = actual_client.analytics.events.create(event)
    assert resp["ok"] is True
    result = actual_client.analytics.events.retrieve(
        user_id="user-1",
        name="company_analytics_rule",
        n=10,
    )
    assert "events" in result


def test_acutal_retrieve_events(
    actual_client: Client,
    delete_all: None,
    create_collection: None,
    delete_all_analytics_rules: None,
) -> None:
    actual_client.analytics.rules.create(
        {
            "name": "company_analytics_rule",
            "type": "log",
            "collection": "companies",
            "event_type": "click",
            "params": {},
        }
    )
    event: AnalyticsEvent = {
        "name": "company_analytics_rule",
        "event_type": "query",
        "data": {
            "user_id": "user-1",
            "doc_id": "apple",
        },
    }
    resp = actual_client.analytics.events.create(event)
    assert resp["ok"] is True
    result = actual_client.analytics.events.retrieve(
        user_id="user-1", name="company_analytics_rule", n=10
    )
    assert "events" in result


def test_acutal_flush(actual_client: Client, delete_all: None) -> None:
    resp = actual_client.analytics.events.flush()
    assert resp["ok"] in [True, False]


async def test_actual_create_event_async(
    actual_async_analytics_rules: AsyncAnalyticsRules,
    actual_async_analytics_events: AsyncAnalyticsEvents,
    delete_all: None,
    create_collection: None,
    delete_all_analytics_rules: None,
) -> None:
    await actual_async_analytics_rules.create(
        {
            "name": "company_analytics_rule",
            "type": "log",
            "collection": "companies",
            "event_type": "click",
            "params": {},
        }
    )
    event: AnalyticsEvent = {
        "name": "company_analytics_rule",
        "event_type": "query",
        "data": {
            "user_id": "user-1",
            "doc_id": "apple",
        },
    }
    resp = await actual_async_analytics_events.create(event)
    assert resp["ok"] is True
    await actual_async_analytics_rules["company_analytics_rule"].delete()


async def test_status_async(
    actual_async_analytics_events: AsyncAnalyticsEvents,
    delete_all: None,
) -> None:
    status = await actual_async_analytics_events.status()
    assert isinstance(status, dict)


async def test_retrieve_events_async(
    actual_async_analytics_rules: AsyncAnalyticsRules,
    actual_async_analytics_events: AsyncAnalyticsEvents,
    delete_all: None,
    create_collection: None,
    delete_all_analytics_rules: None,
) -> None:
    await actual_async_analytics_rules.create(
        {
            "name": "company_analytics_rule",
            "type": "log",
            "collection": "companies",
            "event_type": "click",
            "params": {},
        }
    )
    event: AnalyticsEvent = {
        "name": "company_analytics_rule",
        "event_type": "query",
        "data": {
            "user_id": "user-1",
            "doc_id": "apple",
        },
    }
    resp = await actual_async_analytics_events.create(event)
    assert resp["ok"] is True
    result = await actual_async_analytics_events.retrieve(
        user_id="user-1",
        name="company_analytics_rule",
        n=10,
    )
    assert "events" in result


async def test_actual_flush_async(
    actual_async_analytics_events: AsyncAnalyticsEvents,
    delete_all: None,
) -> None:
    resp = await actual_async_analytics_events.flush()
    assert resp["ok"] in [True, False]
