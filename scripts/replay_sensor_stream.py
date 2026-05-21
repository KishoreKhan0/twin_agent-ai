r"""Replay TwinAgent AI sensor data as MQTT-style messages.

Dry-run mode is enabled by default and does not require Mosquitto:

    python scripts\replay_sensor_stream.py --dry-run --limit-rows 2

For live MQTT publishing, start a broker first and run:

    python scripts\replay_sensor_stream.py --live --limit-rows 10
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from twinagent.streaming import MQTTSensorPublisher  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Replay TwinAgent AI sensor stream.")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "sensor_data_with_anomalies.csv",
        help="Processed CSV to replay.",
    )
    parser.add_argument(
        "--broker-host",
        default="localhost",
        help="MQTT broker hostname.",
    )
    parser.add_argument(
        "--broker-port",
        type=int,
        default=1883,
        help="MQTT broker port.",
    )
    parser.add_argument(
        "--limit-rows",
        type=int,
        default=2,
        help="Number of dataframe rows to replay.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=0.0,
        help="Delay between rows.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Publish to a live MQTT broker instead of dry-run printing.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print MQTT messages without connecting to a broker. This is the default.",
    )
    return parser.parse_args()


def main() -> None:
    """Replay processed data as MQTT-style sensor messages."""
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Input data not found: {args.input}. "
            r"Run python scripts\run_anomaly_detection.py first."
        )

    dataframe = pd.read_csv(args.input)
    publisher = MQTTSensorPublisher(
        broker_host=args.broker_host,
        broker_port=args.broker_port,
    )

    dry_run = not args.live
    messages = publisher.replay_dataframe(
        dataframe,
        dry_run=dry_run,
        limit_rows=args.limit_rows,
        delay_seconds=args.delay_seconds,
    )

    mode = "dry-run" if dry_run else "live MQTT"
    print("TwinAgent AI sensor stream replay complete.")
    print(f"Mode: {mode}")
    print(f"Input rows replayed: {args.limit_rows}")
    print(f"Messages generated: {len(messages)}")

    for topic, message in messages[:12]:
        print(f"{topic} -> {message.to_json()}")

    if len(messages) > 12:
        print(f"... {len(messages) - 12} more messages")


if __name__ == "__main__":
    main()
