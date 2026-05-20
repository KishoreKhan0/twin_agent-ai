"""Plotly chart builders for the TwinAgent AI dashboard."""

from __future__ import annotations

from typing import Iterable

import pandas as pd
import plotly.graph_objects as go


DEFAULT_SENSOR_COLUMNS = [
    "temperature_c",
    "vibration_mm_s",
    "rpm",
    "current_a",
    "load_pct",
    "belt_speed_mps",
    "throughput_units_min",
]


def create_sensor_timeseries_chart(
    dataframe: pd.DataFrame,
    sensor_columns: Iterable[str] | None = None,
) -> go.Figure:
    """Create a multi-sensor time-series line chart."""
    _validate_timestamp_column(dataframe)

    selected_sensors = [
        sensor for sensor in (sensor_columns or DEFAULT_SENSOR_COLUMNS) if sensor in dataframe.columns
    ]
    if not selected_sensors:
        raise ValueError("No valid sensor columns were provided for plotting.")

    figure = go.Figure()

    for sensor in selected_sensors:
        figure.add_trace(
            go.Scatter(
                x=dataframe["timestamp"],
                y=dataframe[sensor],
                mode="lines",
                name=sensor,
            )
        )

    figure.update_layout(
        title="Sensor timeline",
        xaxis_title="Time",
        yaxis_title="Sensor value",
        legend_title="Sensor",
        hovermode="x unified",
    )
    return figure


def create_anomaly_score_chart(dataframe: pd.DataFrame) -> go.Figure:
    """Create an anomaly-score timeline chart."""
    _validate_timestamp_column(dataframe)
    if "anomaly_score" not in dataframe.columns:
        raise ValueError("Dataframe must include anomaly_score.")

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=dataframe["timestamp"],
            y=dataframe["anomaly_score"],
            mode="lines",
            name="anomaly_score",
        )
    )

    figure.add_hline(y=0.25, line_dash="dash", annotation_text="low threshold")
    figure.add_hline(y=0.45, line_dash="dash", annotation_text="medium threshold")
    figure.add_hline(y=0.70, line_dash="dash", annotation_text="high threshold")

    figure.update_layout(
        title="Anomaly score timeline",
        xaxis_title="Time",
        yaxis_title="Anomaly score",
        hovermode="x unified",
    )
    return figure


def create_health_score_chart(dataframe: pd.DataFrame) -> go.Figure:
    """Create a health-score timeline chart."""
    _validate_timestamp_column(dataframe)
    if "health_score" not in dataframe.columns:
        raise ValueError("Dataframe must include health_score.")

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=dataframe["timestamp"],
            y=dataframe["health_score"],
            mode="lines",
            name="health_score",
        )
    )

    figure.add_hline(y=85, line_dash="dash", annotation_text="healthy")
    figure.add_hline(y=70, line_dash="dash", annotation_text="watch")
    figure.add_hline(y=55, line_dash="dash", annotation_text="medium")
    figure.add_hline(y=35, line_dash="dash", annotation_text="critical boundary")

    figure.update_layout(
        title="Machine health score",
        xaxis_title="Time",
        yaxis_title="Health score",
        yaxis_range=[0, 105],
        hovermode="x unified",
    )
    return figure


def filter_time_window(
    dataframe: pd.DataFrame,
    start_time: str | None = None,
    end_time: str | None = None,
) -> pd.DataFrame:
    """Filter a dataframe to a timestamp window."""
    _validate_timestamp_column(dataframe)

    result = dataframe.copy()
    if start_time:
        result = result[result["timestamp"] >= pd.Timestamp(start_time)]
    if end_time:
        result = result[result["timestamp"] <= pd.Timestamp(end_time)]

    if result.empty:
        raise ValueError("Selected time window contains no data.")

    return result


def _validate_timestamp_column(dataframe: pd.DataFrame) -> None:
    """Validate that the dataframe has a timestamp column."""
    if dataframe.empty:
        raise ValueError("Cannot create chart from empty dataframe.")
    if "timestamp" not in dataframe.columns:
        raise ValueError("Dataframe must include timestamp column.")
