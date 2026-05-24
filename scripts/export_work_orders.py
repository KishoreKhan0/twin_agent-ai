r"""Export TwinAgent AI maintenance work orders.

Run from the project root:

    python scripts\export_work_orders.py

By default this exports both local and fleet work-order queues.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.maintenance import export_work_orders  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Export TwinAgent AI work-order queues.")
    parser.add_argument(
        "--local-incidents",
        type=Path,
        default=PROJECT_ROOT / "data" / "incidents" / "incidents.json",
        help="Local incidents JSON path.",
    )
    parser.add_argument(
        "--fleet-incidents",
        type=Path,
        default=PROJECT_ROOT / "data" / "fleet" / "incidents" / "fleet_incidents.json",
        help="Fleet incidents JSON path.",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "reports",
        help="Reports output directory.",
    )
    return parser.parse_args()


def main() -> None:
    """Export local and fleet work-order queues."""
    args = parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)

    if args.local_incidents.exists():
        local_queue = export_work_orders(
            incidents_path=args.local_incidents,
            output_json_path=args.reports_dir / "local_work_orders.json",
            output_markdown_path=args.reports_dir / "local_work_orders.md",
            work_order_prefix="LWO",
        )
        print("Local maintenance work orders exported.")
        print(f"Local work orders: {local_queue.total_work_orders}")
        print(f"Local P1 count: {local_queue.open_p1_count}")
        print(f"Local top priority machine: {local_queue.top_priority_machine}")
    else:
        print(f"Local incidents not found: {args.local_incidents}")

    if args.fleet_incidents.exists():
        fleet_reports_dir = PROJECT_ROOT / "data" / "fleet" / "reports"
        fleet_reports_dir.mkdir(parents=True, exist_ok=True)
        fleet_queue = export_work_orders(
            incidents_path=args.fleet_incidents,
            output_json_path=fleet_reports_dir / "fleet_work_orders.json",
            output_markdown_path=fleet_reports_dir / "fleet_work_orders.md",
            work_order_prefix="FWO",
        )
        print("Fleet maintenance work orders exported.")
        print(f"Fleet work orders: {fleet_queue.total_work_orders}")
        print(f"Fleet P1 count: {fleet_queue.open_p1_count}")
        print(f"Fleet top priority machine: {fleet_queue.top_priority_machine}")
    else:
        print(f"Fleet incidents not found: {args.fleet_incidents}")


if __name__ == "__main__":
    main()
