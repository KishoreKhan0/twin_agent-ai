"""Benchmark runner for TwinAgent AI evaluation metrics."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd

from twinagent.evaluation.metrics import (
    compute_binary_detection_metrics,
    compute_detection_delay,
    compute_fault_classification_summary,
    compute_incident_diagnosis_metrics,
    compute_incident_overlap_score,
)


@dataclass(frozen=True)
class EvaluationBenchmark:
    """Run evaluation metrics over processed sensor data and incidents."""

    processed_data_path: Path
    incidents_path: Path

    def run(self) -> dict[str, Any]:
        """Run all benchmark metrics and return a serializable report."""
        dataframe = self._load_processed_data()
        incidents = self._load_incidents()

        return {
            "summary": {
                "rows": int(len(dataframe)),
                "machine_id": str(dataframe["machine_id"].iloc[0]),
                "time_start": str(dataframe["timestamp"].iloc[0]),
                "time_end": str(dataframe["timestamp"].iloc[-1]),
                "fault_rows": int((dataframe["fault_label"].astype(str) != "normal").sum()),
                "anomaly_rows": int(dataframe["is_anomaly"].astype(bool).sum()),
                "incident_count": len(incidents),
            },
            "binary_detection": compute_binary_detection_metrics(dataframe),
            "detection_delay": compute_detection_delay(dataframe),
            "incident_overlap": compute_incident_overlap_score(dataframe, incidents),
            "row_fault_classification": compute_fault_classification_summary(dataframe),
            "incident_diagnosis": compute_incident_diagnosis_metrics(dataframe, incidents),
        }

    def save_json(self, output_path: str | Path) -> Path:
        """Run benchmark and save JSON results."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        report = self.run()
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return path

    def save_markdown(self, output_path: str | Path) -> Path:
        """Run benchmark and save a human-readable Markdown report."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        report = self.run()
        markdown = self._to_markdown(report)
        path.write_text(markdown, encoding="utf-8")
        return path

    def _load_processed_data(self) -> pd.DataFrame:
        """Load processed anomaly data."""
        if not self.processed_data_path.exists():
            raise FileNotFoundError(
                f"Processed data not found: {self.processed_data_path}. "
                "Run python scripts\\run_anomaly_detection.py first."
            )

        dataframe = pd.read_csv(self.processed_data_path)
        if dataframe.empty:
            raise ValueError(f"Processed data file is empty: {self.processed_data_path}")

        return dataframe

    def _load_incidents(self) -> list[dict[str, Any]]:
        """Load generated incidents."""
        if not self.incidents_path.exists():
            raise FileNotFoundError(
                f"Incidents file not found: {self.incidents_path}. "
                "Run python scripts\\run_anomaly_detection.py first."
            )

        with self.incidents_path.open("r", encoding="utf-8") as file:
            incidents = json.load(file)

        if not isinstance(incidents, list):
            raise ValueError("Incidents JSON must contain a list.")

        return incidents

    @staticmethod
    def _to_markdown(report: dict[str, Any]) -> str:
        """Convert an evaluation report dictionary to Markdown."""
        summary = report["summary"]
        binary = report["binary_detection"]
        delay = report["detection_delay"]
        overlap = report["incident_overlap"]
        row_classification = report["row_fault_classification"]
        incident_diagnosis = report["incident_diagnosis"]

        lines: list[str] = [
            "# TwinAgent AI Evaluation Report",
            "",
            "## Dataset summary",
            "",
            f"- Machine ID: `{summary['machine_id']}`",
            f"- Time range: `{summary['time_start']}` to `{summary['time_end']}`",
            f"- Total rows: **{summary['rows']}**",
            f"- Fault rows: **{summary['fault_rows']}**",
            f"- Anomaly rows: **{summary['anomaly_rows']}**",
            f"- Incidents: **{summary['incident_count']}**",
            "",
            "## Binary anomaly detection metrics",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Precision | {binary['precision']} |",
            f"| Recall | {binary['recall']} |",
            f"| F1 score | {binary['f1_score']} |",
            f"| Accuracy | {binary['accuracy']} |",
            f"| False positive rate | {binary['false_positive_rate']} |",
            f"| True positive | {binary['true_positive']} |",
            f"| False positive | {binary['false_positive']} |",
            f"| True negative | {binary['true_negative']} |",
            f"| False negative | {binary['false_negative']} |",
            "",
            "## Detection delay",
            "",
            f"- Fault episodes: **{delay['fault_episodes']}**",
            f"- Detected episodes: **{delay['detected_episodes']}**",
            f"- Missed episodes: **{delay['missed_episodes']}**",
            f"- Mean detection delay: **{delay['mean_detection_delay_seconds']} seconds**",
            f"- Max detection delay: **{delay['max_detection_delay_seconds']} seconds**",
            "",
            "## Incident overlap",
            "",
            f"- Incident overlap score: **{overlap['incident_overlap_score']}**",
            f"- Ground-truth fault rows: **{overlap['truth_fault_rows']}**",
            f"- Incident-window rows: **{overlap['incident_window_rows']}**",
            f"- Overlap rows: **{overlap['overlap_rows']}**",
            "",
            "## Incident-level diagnosis",
            "",
            f"- Evaluated incidents: **{incident_diagnosis['evaluated_incidents']}**",
            f"- Correct incidents: **{incident_diagnosis['correct_incidents']}**",
            f"- Incident diagnosis accuracy: **{incident_diagnosis['incident_diagnosis_accuracy']}**",
            "",
            "| Incident | Predicted fault | Ground-truth faults | Correct |",
            "|---|---|---|---|",
        ]

        for row in incident_diagnosis["diagnoses"]:
            lines.append(
                f"| {row['incident_id']} | {row['predicted_fault']} | "
                f"{', '.join(row['truth_faults'])} | {row['is_correct']} |"
            )

        lines.extend(
            [
                "",
                "## Row-level suspected-fault alignment",
                "",
                f"- Evaluated anomaly rows inside fault windows: **{row_classification['evaluated_rows']}**",
                f"- Row alignment accuracy: **{row_classification['row_alignment_accuracy']}**",
                "",
                "| Ground-truth fault group | Predicted fault | Count |",
                "|---|---|---:|",
            ]
        )

        for row in row_classification["confusion_matrix"]:
            lines.append(
                f"| {row['truth_fault_group']} | {row['predicted_fault_type']} | {row['count']} |"
            )

        lines.extend(
            [
                "",
                "## Notes",
                "",
                "- These metrics are evaluated against synthetic ground-truth fault labels.",
                "- Incident-level diagnosis is the most relevant diagnosis metric for the current MVP because the copilot explains incidents.",
                "- Row-level suspected-fault alignment is stricter and can be lower during overlapping or evolving fault windows.",
                "- The detector is an interpretable prototype using threshold-based anomaly logic.",
                "- The results should not be described as real-world predictive-maintenance accuracy.",
                "",
            ]
        )

        return "\n".join(lines)
