r"""Run the full TwinAgent AI backend pipeline.

This is the production-style one-command runner.

Typical full run:

    python scripts\run_full_pipeline.py

With tests first:

    python scripts\run_full_pipeline.py --include-tests

Local-only run without fleet generation:

    python scripts\run_full_pipeline.py --local-only
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.pipeline import PipelineConfig, run_full_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Run the full TwinAgent AI backend pipeline.")
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Run pytest before the pipeline.",
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Skip fleet generation/analysis/triage and run only the local ML pipeline.",
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Continue running later steps even if one step fails.",
    )
    return parser.parse_args()


def main() -> None:
    """Run full pipeline and print concise summary."""
    args = parse_args()

    config = PipelineConfig(
        project_root=PROJECT_ROOT,
        python_executable=sys.executable,
        include_tests=args.include_tests,
        include_fleet=not args.local_only,
        stop_on_failure=not args.continue_on_failure,
        write_summary=True,
    )

    result = run_full_pipeline(config)

    print("TwinAgent AI full pipeline complete.")
    print(f"Status: {result.status}")
    print(f"Duration seconds: {result.duration_seconds}")
    print("Step summary:")

    for step in result.steps:
        icon = "OK" if step.status == "passed" else "FAIL"
        print(f"- {icon} | {step.name} | {step.duration_seconds}s")
        if step.status != "passed":
            print(f"  Return code: {step.return_code}")
            if step.missing_outputs:
                print(f"  Missing outputs: {step.missing_outputs}")
            if step.stderr_tail:
                print("  stderr tail:")
                print(step.stderr_tail)

    local = result.artifact_summary.get("local", {})
    fleet = result.artifact_summary.get("fleet", {})
    ml = result.artifact_summary.get("ml", {})
    reports = result.artifact_summary.get("reports", {})

    print("Artifact summary:")
    print(f"- Local incidents: {local.get('incident_count', 0)}")
    print(f"- Reconciled incidents: {local.get('reconciled_incident_count', 0)}")
    print(f"- Fleet machines: {fleet.get('machine_count', 0)}")
    print(f"- Fleet incidents: {fleet.get('incident_count', 0)}")
    print(f"- ML windows/classes: {ml.get('window_count', 0)} / {ml.get('class_count', 0)}")
    print(f"- ML weighted F1: {ml.get('weighted_f1')}")
    print(f"- Local work orders: {reports.get('local_work_orders', 0)}")
    print(f"- Fleet work orders: {reports.get('fleet_work_orders', 0)}")
    print(r"Summary JSON: data\reports\pipeline_run_summary.json")
    print(r"Summary Markdown: data\reports\pipeline_run_summary.md")

    if result.status != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
