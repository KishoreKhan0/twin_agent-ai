"""Conversation memory for the TwinAgent AI copilot."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3


CREATE_MEMORY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS copilot_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    incident_id TEXT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    intent TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class CopilotMemory:
    """Small SQLite-backed memory store for copilot Q&A."""

    database_path: Path

    def initialize(self) -> None:
        """Create memory table if needed."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(CREATE_MEMORY_TABLE_SQL)
            connection.commit()

    def add_interaction(
        self,
        question: str,
        answer: str,
        intent: str,
        provider: str,
        model: str,
        incident_id: str | None = None,
    ) -> None:
        """Persist one copilot interaction."""
        self.initialize()
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO copilot_memory (
                    created_at, incident_id, question, answer, intent, provider, model
                )
                VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (created_at, incident_id, question, answer, intent, provider, model),
            )
            connection.commit()

    def recent_interactions(self, limit: int = 5, incident_id: str | None = None) -> list[dict]:
        """Return recent copilot interactions."""
        self.initialize()

        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            if incident_id:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM copilot_memory
                    WHERE incident_id = ?
                    ORDER BY id DESC
                    LIMIT ?;
                    """,
                    (incident_id, limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM copilot_memory
                    ORDER BY id DESC
                    LIMIT ?;
                    """,
                    (limit,),
                ).fetchall()

        return [dict(row) for row in rows]
