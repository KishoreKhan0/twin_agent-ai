"""SQLite database setup for TwinAgent AI."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from twinagent.storage.schemas import (
    CREATE_INCIDENTS_TABLE_SQL,
    CREATE_INDEXES_SQL,
    CREATE_METADATA_TABLE_SQL,
    CREATE_SENSOR_READINGS_TABLE_SQL,
)


def connect_database(database_path: str | Path) -> sqlite3.Connection:
    """Create a SQLite connection with sensible defaults."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def initialize_database(database_path: str | Path) -> Path:
    """Create SQLite tables and indexes if they do not already exist."""
    path = Path(database_path)
    with connect_database(path) as connection:
        connection.execute(CREATE_SENSOR_READINGS_TABLE_SQL)
        connection.execute(CREATE_INCIDENTS_TABLE_SQL)
        connection.execute(CREATE_METADATA_TABLE_SQL)

        for statement in CREATE_INDEXES_SQL:
            connection.execute(statement)

        connection.execute(
            """
            INSERT OR REPLACE INTO metadata(key, value)
            VALUES ('schema_version', '1');
            """
        )
        connection.commit()

    return path
