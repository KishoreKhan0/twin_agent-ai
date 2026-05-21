"""SQLite schema constants for TwinAgent AI."""

from __future__ import annotations


SENSOR_READING_COLUMNS = [
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
    "temperature_c_anomaly_score",
    "temperature_c_rolling_z",
    "vibration_mm_s_anomaly_score",
    "vibration_mm_s_rolling_z",
    "current_a_anomaly_score",
    "current_a_rolling_z",
    "rpm_anomaly_score",
    "rpm_rolling_z",
    "throughput_units_min_anomaly_score",
    "throughput_units_min_rolling_z",
    "anomaly_score",
    "is_anomaly",
    "anomaly_severity",
    "contributing_sensors",
    "suspected_fault",
    "health_score",
    "risk_level",
    "maintenance_urgency",
    "maintenance_recommendation",
]


INCIDENT_COLUMNS = [
    "incident_id",
    "machine_id",
    "start_time",
    "end_time",
    "duration_seconds",
    "severity",
    "suspected_fault",
    "max_anomaly_score",
    "mean_anomaly_score",
    "contributing_sensors_json",
    "evidence_json",
]


CREATE_SENSOR_READINGS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    machine_id TEXT NOT NULL,
    temperature_c REAL,
    vibration_mm_s REAL,
    rpm REAL,
    current_a REAL,
    load_pct REAL,
    belt_speed_mps REAL,
    throughput_units_min REAL,
    ambient_temperature_c REAL,
    operating_mode TEXT,
    machine_state TEXT,
    fault_label TEXT,
    fault_severity TEXT,
    temperature_c_anomaly_score REAL,
    temperature_c_rolling_z REAL,
    vibration_mm_s_anomaly_score REAL,
    vibration_mm_s_rolling_z REAL,
    current_a_anomaly_score REAL,
    current_a_rolling_z REAL,
    rpm_anomaly_score REAL,
    rpm_rolling_z REAL,
    throughput_units_min_anomaly_score REAL,
    throughput_units_min_rolling_z REAL,
    anomaly_score REAL,
    is_anomaly INTEGER,
    anomaly_severity TEXT,
    contributing_sensors TEXT,
    suspected_fault TEXT,
    health_score INTEGER,
    risk_level TEXT,
    maintenance_urgency TEXT,
    maintenance_recommendation TEXT
);
"""


CREATE_INCIDENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS incidents (
    incident_id TEXT PRIMARY KEY,
    machine_id TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    duration_seconds INTEGER,
    severity TEXT,
    suspected_fault TEXT,
    max_anomaly_score REAL,
    mean_anomaly_score REAL,
    contributing_sensors_json TEXT,
    evidence_json TEXT
);
"""


CREATE_METADATA_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_sensor_readings_machine_time "
    "ON sensor_readings(machine_id, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_sensor_readings_anomaly "
    "ON sensor_readings(is_anomaly);",
    "CREATE INDEX IF NOT EXISTS idx_sensor_readings_fault "
    "ON sensor_readings(fault_label);",
    "CREATE INDEX IF NOT EXISTS idx_incidents_machine_time "
    "ON incidents(machine_id, start_time);",
]
