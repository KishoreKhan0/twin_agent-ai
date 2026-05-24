r"""Generate synthetic conveyor-motor sensor data for TwinAgent AI.

Run from the project root:

    python scripts\generate_synthetic_data.py

By default this now uses configs/local_demo_config.yaml, which is a larger
single-machine demo with multiple fault windows. The original compact config is
still available at configs/machine_config.yaml for unit tests and small demos.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.simulation import MachineSimulator  # noqa: E402


def default_config_path() -> Path:
    """Return preferred local demo config path."""
    rich_config = PROJECT_ROOT / "configs" / "local_demo_config.yaml"
    if rich_config.exists():
        return rich_config
    return PROJECT_ROOT / "configs" / "machine_config.yaml"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate synthetic TwinAgent AI sensor data.")
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config_path(),
        help="Path to the machine YAML config.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "generated" / "sensor_data.csv",
        help="Path where the generated CSV should be saved.",
    )
    return parser.parse_args()


def main() -> None:
    """Generate the dataset, save it once, and print a matching summary."""
    args = parse_args()

    simulator = MachineSimulator.from_config_file(args.config)
    dataframe = simulator.simulate()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(args.output, index=False)

    fault_counts = dataframe["fault_label"].value_counts().to_dict()
    state_counts = dataframe["machine_state"].value_counts().to_dict()

    print("TwinAgent AI synthetic data generation complete.")
    print(f"Config used: {args.config}")
    print(f"Machine ID: {simulator.machine_id}")
    print(f"Rows generated: {len(dataframe)}")
    print(f"Time range: {dataframe['timestamp'].iloc[0]} -> {dataframe['timestamp'].iloc[-1]}")
    print(f"Fault label counts: {fault_counts}")
    print(f"Machine state counts: {state_counts}")
    print(f"Saved CSV: {args.output}")


if __name__ == "__main__":
    main()
