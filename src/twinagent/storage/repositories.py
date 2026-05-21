"""SQLite repository layer for TwinAgent AI."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd

from twinagent.storage.database import connect_database, initialize_database
from twinagent.storage.schemas import INCIDENT_COLUMNS, SENSOR_READING_COLUMNS


@dataclass(frozen=True)
class SQLiteRepository:
    """Repository for persisting and querying TwinAgent AI outputs."""

    database_path: Path

    def initialize(self) -> Path:
        """Initialize the database schema."""
        return initialize_database(self.database_path)

    def clear_all(self) -> None:
        """Delete all persisted rows from known project tables."""
        self.initialize()
        with connect_database(self.database_path) as connection:
            connection.execute("DELETE FROM sensor_readings;")
            connection.execute("DELETE FROM incidents;")
            connection.commit()

    def write_sensor_readings(self, dataframe: pd.DataFrame, replace: bool = True) -> int:
        """Persist processed sensor readings to SQLite."""
        if dataframe.empty:
            raise ValueError("Cannot write an empty sensor dataframe to SQLite.")

        missing = set(SENSOR_READING_COLUMNS) - set(dataframe.columns)
        if missing:
            raise ValueError(
                "Sensor dataframe is missing required columns: "
                + ", ".join(sorted(missing))
            )

        self.initialize()
        normalized = dataframe[SENSOR_READING_COLUMNS].copy()
        normalized["timestamp"] = pd.to_datetime(normalized["timestamp"]).dt.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        normalized["is_anomaly"] = normalized["is_anomaly"].astype(bool).astype(int)

        with connect_database(self.database_path) as connection:
            if replace:
                connection.execute("DELETE FROM sensor_readings;")

            normalized.to_sql(
                "sensor_readings",
                connection,
                if_exists="append",
                index=False,
            )
            connection.commit()

        return int(len(normalized))

    def write_incidents(self, incidents: list[dict[str, Any]], replace: bool = True) -> int:
        """Persist incident records to SQLite."""
        self.initialize()

        rows = [self._incident_to_row(incident) for incident in incidents]

        with connect_database(self.database_path) as connection:
            if replace:
                connection.execute("DELETE FROM incidents;")

            if rows:
                placeholders = ", ".join(["?"] * len(INCIDENT_COLUMNS))
                columns = ", ".join(INCIDENT_COLUMNS)
                connection.executemany(
                    f"INSERT OR REPLACE INTO incidents ({columns}) VALUES ({placeholders});",
                    [[row[column] for column in INCIDENT_COLUMNS] for row in rows],
                )

            connection.commit()

        return len(rows)

    def get_sensor_row_count(self) -> int:
        """Return number of persisted sensor readings."""
        self.initialize()
        with connect_database(self.database_path) as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM sensor_readings;").fetchone()
        return int(row["count"])

    def get_incident_count(self) -> int:
        """Return number of persisted incidents."""
        self.initialize()
        with connect_database(self.database_path) as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM incidents;").fetchone()
        return int(row["count"])

    def get_latest_machine_state(self, machine_id: str) -> dict[str, Any]:
        """Return the latest persisted row for a machine."""
        self.initialize()
        with connect_database(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT *
                FROM sensor_readings
                WHERE machine_id = ?
                ORDER BY timestamp DESC
                LIMIT 1;
                """,
                (machine_id,),
            ).fetchone()

        if row is None:
            raise ValueError(f"No sensor readings found for machine_id={machine_id!r}.")

        return dict(row)

    def query_sensor_window(
        self,
        machine_id: str,
        start_time: str,
        end_time: str,
    ) -> pd.DataFrame:
        """Return persisted sensor readings for a machine and time window."""
        self.initialize()
        with connect_database(self.database_path) as connection:
            dataframe = pd.read_sql_query(
                """
                SELECT *
                FROM sensor_readings
                WHERE machine_id = ?
                  AND timestamp >= ?
                  AND timestamp <= ?
                ORDER BY timestamp ASC;
                """,
                connection,
                params=(machine_id, start_time, end_time),
            )

        if dataframe.empty:
            raise ValueError(
                f"No sensor readings found for {machine_id} between {start_time} and {end_time}."
            )

        return dataframe

    def get_incident(self, incident_id: str) -> dict[str, Any]:
        """Return one incident by ID."""
        self.initialize()
        with connect_database(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT *
                FROM incidents
                WHERE incident_id = ?;
                """,
                (incident_id,),
            ).fetchone()

        if row is None:
            raise ValueError(f"Incident not found: {incident_id}")

        return self._row_to_incident(dict(row))

    def list_incidents(self, machine_id: str | None = None) -> list[dict[str, Any]]:
        """List incidents, optionally filtered by machine."""
        self.initialize()
        with connect_database(self.database_path) as connection:
            if machine_id:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM incidents
                    WHERE machine_id = ?
                    ORDER BY start_time ASC;
                    """,
                    (machine_id,),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM incidents
                    ORDER BY start_time ASC;
                    """
                ).fetchall()

        return [self._row_to_incident(dict(row)) for row in rows]

    @staticmethod
    def _incident_to_row(incident: dict[str, Any]) -> dict[str, Any]:
        """Normalize one incident dictionary for SQLite storage."""
        return {
            "incident_id": incident["incident_id"],
            "machine_id": incident["machine_id"],
            "start_time": incident["start_time"],
            "end_time": incident["end_time"],
            "duration_seconds": int(incident.get("duration_seconds", 0)),
            "severity": incident.get("severity", "unknown"),
            "suspected_fault": incident.get("suspected_fault", "unknown"),
            "max_anomaly_score": float(incident.get("max_anomaly_score", 0.0)),
            "mean_anomaly_score": float(incident.get("mean_anomaly_score", 0.0)),
            "contributing_sensors_json": json.dumps(
                incident.get("contributing_sensors", []),
                sort_keys=True,
            ),
            "evidence_json": json.dumps(
                incident.get("evidence", {}),
                sort_keys=True,
            ),
        }

    @staticmethod
    def _row_to_incident(row: dict[str, Any]) -> dict[str, Any]:
        """Convert a SQLite row dictionary back into an incident dictionary."""
        return {
            "incident_id": row["incident_id"],
            "machine_id": row["machine_id"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "duration_seconds": int(row["duration_seconds"]),
            "severity": row["severity"],
            "suspected_fault": row["suspected_fault"],
            "max_anomaly_score": float(row["max_anomaly_score"]),
            "mean_anomaly_score": float(row["mean_anomaly_score"]),
            "contributing_sensors": json.loads(row["contributing_sensors_json"] or "[]"),
            "evidence": json.loads(row["evidence_json"] or "{}"),
        }
