"""Unit tests for per-rule AnalyticsRule operations."""

import pytest

from tests.utils.version import is_v30_or_above
from typesense.sync.client import Client
from typesense.sync.analytics_rules import AnalyticsRules
from typesense.async_.analytics_rules import AsyncAnalyticsRules


pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run analytics tests only on v30+",
)


def test_actual_rule_retrieve(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    resp = actual_analytics_rules["company_analytics_rule"].retrieve()
    assert resp["name"] == "company_analytics_rule"


def test_actual_rule_delete(
    actual_analytics_rules: AnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    resp = actual_analytics_rules["company_analytics_rule"].delete()
    assert resp["name"] == "company_analytics_rule"


async def test_actual_rule_retrieve_async(
    actual_async_analytics_rules: AsyncAnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    resp = await actual_async_analytics_rules["company_analytics_rule"].retrieve()
    assert resp["name"] == "company_analytics_rule"


async def test_actual_rule_delete_async(
    actual_async_analytics_rules: AsyncAnalyticsRules,
    delete_all: None,
    delete_all_analytics_rules: None,
    create_analytics_rule: None,
) -> None:
    resp = await actual_async_analytics_rules["company_analytics_rule"].delete()
    assert resp["name"] == "company_analytics_rule"
