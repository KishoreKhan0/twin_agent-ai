"""Tests for API smoke-test request definitions."""

from __future__ import annotations

from scripts.smoke_test_api import DEFAULT_CHECKS


def test_smoke_test_includes_core_endpoints() -> None:
    paths = {check.path for check in DEFAULT_CHECKS}

    assert "/health" in paths
    assert "/summary" in paths
    assert "/incidents/reconciled" in paths
    assert "/ml/metrics" in paths
    assert "/work-orders/local" in paths
    assert "/fleet/summary" in paths
    assert "/work-orders/fleet" in paths


def test_smoke_test_has_post_agent_question() -> None:
    check = next(item for item in DEFAULT_CHECKS if item.path == "/agent/incident-question")

    assert check.method == "POST"
    assert check.json_body is not None
    assert check.json_body["incident_id"] == "INC-0001"
