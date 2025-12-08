"""Tests for the AnalyticsRuleV1 class."""

from __future__ import annotations

import pytest

from tests.utils.object_assertions import assert_match_object, assert_object_lists_match
from tests.utils.version import is_v30_or_above
from typesense.client import Client
from typesense.analytics_rule_v1 import AnalyticsRuleV1
from typesense.analytics_rules_v1 import AnalyticsRulesV1
from typesense.api_call import ApiCall
from typesense.async_analytics_rules_v1 import AsyncAnalyticsRulesV1
from typesense.types.analytics_rule_v1 import RuleDeleteSchema, RuleSchemaForQueries

pytestmark = pytest.mark.skipif(
    is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Skip AnalyticsV1 tests on v30+",
)


def test_init(fake_api_call: ApiCall) -> None:
    """Test that the AnalyticsRuleV1 object is initialized correctly."""
    analytics_rule = AnalyticsRuleV1(fake_api_call, "company_analytics_rule")

    assert analytics_rule.rule_id == "company_analytics_rule"
    assert_match_object(analytics_rule.api_call, fake_api_call)
    assert_object_lists_match(
        analytics_rule.api_call.node_manager.nodes,
        fake_api_call.node_manager.nodes,
    )
    assert_match_object(
        analytics_rule.api_call.config.nearest_node,
        fake_api_call.config.nearest_node,
    )
    assert (
        analytics_rule._endpoint_path  # noqa: WPS437
        == "/analytics/rules/company_analytics_rule"
    )


def test_actual_retrieve(
    actual_analytics_rules: AnalyticsRulesV1,
    delete_all: None,
    delete_all_analytics_rules_v1: None,
    create_analytics_rule_v1: None,
) -> None:
    """Test that the AnalyticsRuleV1 object can retrieve a rule from Typesense Server."""
    response = actual_analytics_rules["company_analytics_rule"].retrieve()

    expected: RuleSchemaForQueries = {
        "name": "company_analytics_rule",
        "params": {
            "destination": {"collection": "companies_queries"},
            "limit": 1000,
            "source": {"collections": ["companies"]},
        },
        "type": "nohits_queries",
    }

    assert response == expected


def test_actual_delete(
    actual_analytics_rules: AnalyticsRulesV1,
    delete_all: None,
    delete_all_analytics_rules_v1: None,
    create_analytics_rule_v1: None,
) -> None:
    """Test that the AnalyticsRuleV1 object can delete a rule from Typesense Server."""
    response = actual_analytics_rules["company_analytics_rule"].delete()

    expected: RuleDeleteSchema = {
        "name": "company_analytics_rule",
    }
    assert response == expected


async def test_actual_retrieve_async(
    actual_async_analytics_rules_v1: AsyncAnalyticsRulesV1,
    delete_all: None,
    delete_all_analytics_rules_v1: None,
    create_analytics_rule_v1: None,
) -> None:
    """Test that the AsyncAnalyticsRuleV1 object can retrieve a rule from Typesense Server."""
    response = await actual_async_analytics_rules_v1[
        "company_analytics_rule"
    ].retrieve()

    expected: RuleSchemaForQueries = {
        "name": "company_analytics_rule",
        "params": {
            "destination": {"collection": "companies_queries"},
            "limit": 1000,
            "source": {"collections": ["companies"]},
        },
        "type": "nohits_queries",
    }

    assert response == expected


async def test_actual_delete_async(
    actual_async_analytics_rules_v1: AsyncAnalyticsRulesV1,
    delete_all: None,
    delete_all_analytics_rules_v1: None,
    create_analytics_rule_v1: None,
) -> None:
    """Test that the AsyncAnalyticsRuleV1 object can delete a rule from Typesense Server."""
    response = await actual_async_analytics_rules_v1["company_analytics_rule"].delete()

    expected: RuleDeleteSchema = {
        "name": "company_analytics_rule",
    }
    assert response == expected
