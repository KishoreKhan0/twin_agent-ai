"""Tests for the TwinAgent AI conveyor-motor simulator."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from twinagent.simulation.machine_simulator import MachineSimulator


def _config_path() -> Path:
    return Path(__file__).resolve().parents[1] / "configs" / "machine_config.yaml"


def test_simulator_generates_expected_number_of_rows() -> None:
    simulator = MachineSimulator.from_config_file(_config_path())

    dataframe = simulator.simulate()

    assert len(dataframe) == 60 * 60


def test_simulator_outputs_required_columns() -> None:
    simulator = MachineSimulator.from_config_file(_config_path())

    dataframe = simulator.simulate()

    expected_columns = {
        "timestamp",
        "machine_id",
        "temperature_c",
        "vibration_mm_s",
        "rpm",
        "current_a",
        "load_pct",
        "belt_speed_mps",
        "throughput_units_min",
        "ambient_temperature_c",
        "operating_mode",
        "machine_state",
        "fault_label",
        "fault_severity",
    }

    assert expected_columns.issubset(set(dataframe.columns))


def test_simulator_includes_configured_fault_labels() -> None:
    simulator = MachineSimulator.from_config_file(_config_path())

    dataframe = simulator.simulate()
    fault_labels = set(dataframe["fault_label"].unique())

    assert "normal" in fault_labels
    assert any("bearing_wear" in label for label in fault_labels)
    assert any("overheating" in label for label in fault_labels)
    assert any("belt_misalignment" in label for label in fault_labels)


def test_simulator_can_save_csv(tmp_path: Path) -> None:
    simulator = MachineSimulator.from_config_file(_config_path())
    output_path = tmp_path / "sensor_data.csv"

    saved_path = simulator.save_csv(output_path)

    assert saved_path.exists()

    dataframe = pd.read_csv(saved_path)
    assert len(dataframe) == 60 * 60
    assert dataframe["machine_id"].nunique() == 1
    assert dataframe["machine_id"].iloc[0] == "line1_motor1"
