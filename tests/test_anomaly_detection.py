"""Tests for TwinAgent AI anomaly detection."""

from __future__ import annotations

from pathlib import Path

from twinagent.analytics.anomaly_detection import AnomalyDetector
from twinagent.simulation.machine_simulator import MachineSimulator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_anomaly_detector_adds_expected_columns() -> None:
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate()

    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    processed = detector.detect(dataframe)

    assert "anomaly_score" in processed.columns
    assert "is_anomaly" in processed.columns
    assert "anomaly_severity" in processed.columns
    assert "suspected_fault" in processed.columns
    assert "contributing_sensors" in processed.columns


def test_anomaly_detector_finds_fault_window_anomalies() -> None:
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate()

    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    processed = detector.detect(dataframe)

    fault_rows = processed[processed["fault_label"] != "normal"]
    normal_rows = processed[processed["fault_label"] == "normal"]

    assert fault_rows["is_anomaly"].sum() > 0
    assert fault_rows["anomaly_score"].mean() > normal_rows["anomaly_score"].mean()


def test_anomaly_detector_does_not_flag_every_row() -> None:
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate()

    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    processed = detector.detect(dataframe)

    anomaly_ratio = processed["is_anomaly"].mean()

    assert 0.05 < anomaly_ratio < 0.60


def test_anomaly_detector_keeps_normal_false_positive_rate_reasonable() -> None:
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate()

    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    processed = detector.detect(dataframe)

    normal_rows = processed[processed["fault_label"] == "normal"]
    normal_false_positive_rate = normal_rows["is_anomaly"].mean()

    assert normal_false_positive_rate < 0.10


def test_anomaly_detector_assigns_non_normal_suspected_faults() -> None:
    simulator = MachineSimulator.from_config_file(PROJECT_ROOT / "configs" / "machine_config.yaml")
    dataframe = simulator.simulate()

    detector = AnomalyDetector.from_config_file(PROJECT_ROOT / "configs" / "anomaly_config.yaml")
    processed = detector.detect(dataframe)

    suspected_faults = set(processed.loc[processed["is_anomaly"], "suspected_fault"].unique())

    assert len(suspected_faults - {"normal"}) > 0
