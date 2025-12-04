"""Tests for SynonymSet item-level APIs."""

from __future__ import annotations

import pytest
import requests_mock

from tests.utils.version import is_v30_or_above
from typesense.client import Client
from typesense.synonym_set import SynonymSet
from typesense.types.synonym_set import (
    SynonymItemDeleteSchema,
    SynonymItemSchema,
)

pytestmark = pytest.mark.skipif(
    not is_v30_or_above(
        Client(
            {
                "api_key": "xyz",
                "nodes": [{"host": "localhost", "port": 8108, "protocol": "http"}],
            }
        )
    ),
    reason="Run synonym set items tests only on v30+",
)


    ]


    }


    payload: SynonymItemSchema = {
    }


