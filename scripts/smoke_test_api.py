r"""Smoke-test the running TwinAgent AI API.

Run after starting the API locally or through Docker:

    python scripts\smoke_test_api.py
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class EndpointCheck:
    """One API endpoint smoke-test check."""

    name: str
    method: str
    path: str
    expected_status: int = 200
    json_body: dict[str, Any] | None = None
    params: dict[str, Any] | None = None


DEFAULT_CHECKS = [
    EndpointCheck("landing", "GET", "/"),
    EndpointCheck("health", "GET", "/health"),
    EndpointCheck("summary", "GET", "/summary"),
    EndpointCheck("artifact_status", "GET", "/artifacts/status"),
    EndpointCheck("pipeline_summary", "GET", "/pipeline/summary"),
    EndpointCheck("machine_status", "GET", "/machine/status"),
    EndpointCheck("latest_machine", "GET", "/machines/latest", params={"machine_id": "line1_motor1"}),
    EndpointCheck(
        "machine_window",
        "GET",
        "/machines/line1_motor1/window",
        params={
            "start_time": "2026-05-20T14:37:22",
            "end_time": "2026-05-20T14:37:30",
            "limit": 5,
        },
    ),
    EndpointCheck("incidents", "GET", "/incidents"),
    EndpointCheck("reconciled_incidents", "GET", "/incidents/reconciled"),
    EndpointCheck("incident_detail", "GET", "/incidents/INC-0001"),
    EndpointCheck(
        "agent_incident_question",
        "POST",
        "/agent/incident-question",
        json_body={
            "incident_id": "INC-0001",
            "question": "Why did this incident trigger?",
            "copilot_mode": "deterministic",
        },
    ),
    EndpointCheck("ml_metrics", "GET", "/ml/metrics"),
    EndpointCheck("ml_error_analysis", "GET", "/ml/error-analysis"),
    EndpointCheck("ml_feature_importance", "GET", "/ml/feature-importance", params={"limit": 10}),
    EndpointCheck("local_work_orders", "GET", "/work-orders/local"),
    EndpointCheck("fleet_summary", "GET", "/fleet/summary"),
    EndpointCheck("fleet_incidents", "GET", "/fleet/incidents"),
    EndpointCheck("fleet_triage", "GET", "/fleet/triage"),
    EndpointCheck("fleet_analysis", "GET", "/fleet/analysis"),
    EndpointCheck("fleet_work_orders", "GET", "/work-orders/fleet"),
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Smoke-test the TwinAgent AI API.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base API URL.")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP request timeout in seconds.")
    return parser.parse_args()


def main() -> None:
    """Run all smoke-test checks."""
    args = parse_args()
    base_url = args.base_url.rstrip("/")

    print("TwinAgent AI API smoke test starting.")
    print(f"Base URL: {base_url}")

    failures: list[str] = []

    for check in DEFAULT_CHECKS:
        url = f"{base_url}{check.path}"
        try:
            response = _request(check, url, timeout=args.timeout)
            if response.status_code == check.expected_status:
                print(f"OK   {check.method:<4} {check.path:<38} {response.status_code}")
                _print_compact_signal(check.name, _safe_json(response))
            else:
                message = (
                    f"FAIL {check.method:<4} {check.path:<38} "
                    f"expected {check.expected_status}, got {response.status_code}"
                )
                print(message)
                print(response.text[:500])
                failures.append(message)
        except requests.RequestException as error:
            message = f"FAIL {check.method:<4} {check.path:<38} request error: {error}"
            print(message)
            failures.append(message)

    if failures:
        print("\nTwinAgent AI API smoke test failed.")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("\nTwinAgent AI API smoke test passed.")


def _request(check: EndpointCheck, url: str, *, timeout: float) -> requests.Response:
    """Execute one request."""
    if check.method == "GET":
        return requests.get(url, params=check.params, timeout=timeout)
    if check.method == "POST":
        return requests.post(url, params=check.params, json=check.json_body, timeout=timeout)
    raise ValueError(f"Unsupported method: {check.method}")


def _safe_json(response: requests.Response) -> Any:
    """Return response JSON if possible."""
    try:
        return response.json()
    except ValueError:
        return None


def _print_compact_signal(name: str, payload: Any) -> None:
    """Print compact useful signals for important endpoints."""
    if not isinstance(payload, dict):
        return

    if name == "health":
        print(
            "     "
            f"artifact_status={payload.get('artifact_status')} "
            f"sensor_rows={payload.get('sensor_rows')} "
            f"incident_count={payload.get('incident_count')}"
        )
    elif name == "summary":
        print(
            "     "
            f"reconciled={payload.get('reconciled_incidents')} "
            f"fleet_machines={payload.get('fleet_machines')} "
            f"fleet_incidents={payload.get('fleet_incidents')} "
            f"ml_f1={payload.get('ml_weighted_f1')}"
        )
    elif name == "ml_metrics":
        print(
            "     "
            f"windows={payload.get('window_count')} "
            f"classes={payload.get('class_count')} "
            f"weighted_f1={payload.get('weighted_f1')}"
        )
    elif name in {"local_work_orders", "fleet_work_orders"}:
        print(f"     work_orders={payload.get('total_work_orders')}")
    elif name == "fleet_summary":
        fleet = payload.get("fleet", {})
        print(
            "     "
            f"machines={fleet.get('machine_count')} "
            f"incidents={fleet.get('incident_rows')} "
            f"rows={fleet.get('sensor_rows')}"
        )


if __name__ == "__main__":
    main()
