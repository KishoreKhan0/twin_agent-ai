"""Shared FastAPI dependencies for TwinAgent AI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from twinagent.agent import TwinAgentCopilot
from twinagent.storage import SQLiteRepository


@dataclass(frozen=True)
class ApiContext:
    """Runtime context shared across FastAPI routes."""

    project_root: Path

    @property
    def database_path(self) -> Path:
        """Path to the SQLite database."""
        return self.project_root / "data" / "processed" / "twinagent.db"

    @property
    def processed_data_path(self) -> Path:
        """Path to processed CSV output."""
        return self.project_root / "data" / "processed" / "sensor_data_with_anomalies.csv"

    @property
    def incidents_path(self) -> Path:
        """Path to generated incidents JSON."""
        return self.project_root / "data" / "incidents" / "incidents.json"

    def repository(self) -> SQLiteRepository:
        """Create a SQLite repository for the current project root."""
        return SQLiteRepository(database_path=self.database_path)

    def copilot(self) -> TwinAgentCopilot:
        """Create a copilot using the current project root."""
        return TwinAgentCopilot.from_project_root(self.project_root)


def default_project_root() -> Path:
    """Return the project root based on this file location."""
    return Path(__file__).resolve().parents[3]
