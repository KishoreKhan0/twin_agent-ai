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


PREMIUM_TEMPLATE = "plotly_dark"
PREMIUM_COLORS = [
    "#58a6ff",
    "#35d0ff",
    "#50fa7b",
    "#ffca58",
    "#ff6b6b",
    "#a78bfa",
    "#f472b6",
]


def create_sensor_timeseries_chart(
    dataframe: pd.DataFrame,
    sensor_columns: Iterable[str] | None = None,
) -> go.Figure:
    """Create a premium multi-sensor time-series line chart."""
    _validate_timestamp_column(dataframe)

    selected_sensors = [
        sensor for sensor in (sensor_columns or DEFAULT_SENSOR_COLUMNS) if sensor in dataframe.columns
    ]
    if not selected_sensors:
        raise ValueError("No valid sensor columns were provided for plotting.")

    figure = go.Figure()

    for index, sensor in enumerate(selected_sensors):
        figure.add_trace(
            go.Scatter(
                x=dataframe["timestamp"],
                y=dataframe[sensor],
                mode="lines",
                name=sensor,
                line={
                    "width": 2.4,
                    "color": PREMIUM_COLORS[index % len(PREMIUM_COLORS)],
                },
            )
        )

    _apply_premium_layout(
        figure,
        title="Sensor timeline",
        yaxis_title="Sensor value",
    )
    return figure


def create_anomaly_score_chart(dataframe: pd.DataFrame) -> go.Figure:
    """Create a premium anomaly-score timeline chart."""
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
            line={"width": 3.0, "color": "#ffca58"},
            fill="tozeroy",
            fillcolor="rgba(255, 202, 88, 0.12)",
        )
    )

    figure.add_hline(y=0.25, line_dash="dash", line_color="#58a6ff", annotation_text="low")
    figure.add_hline(y=0.45, line_dash="dash", line_color="#ffca58", annotation_text="medium")
    figure.add_hline(y=0.70, line_dash="dash", line_color="#ff6b6b", annotation_text="high")

    _apply_premium_layout(
        figure,
        title="Anomaly score timeline",
        yaxis_title="Anomaly score",
    )
    figure.update_yaxes(range=[0, 1.05])
    return figure


def create_health_score_chart(dataframe: pd.DataFrame) -> go.Figure:
    """Create a premium health-score timeline chart."""
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
            line={"width": 3.0, "color": "#50fa7b"},
            fill="tozeroy",
            fillcolor="rgba(80, 250, 123, 0.10)",
        )
    )

    figure.add_hline(y=85, line_dash="dash", line_color="#50fa7b", annotation_text="healthy")
    figure.add_hline(y=70, line_dash="dash", line_color="#58a6ff", annotation_text="watch")
    figure.add_hline(y=55, line_dash="dash", line_color="#ffca58", annotation_text="medium")
    figure.add_hline(y=35, line_dash="dash", line_color="#ff6b6b", annotation_text="critical")

    _apply_premium_layout(
        figure,
        title="Machine health score",
        yaxis_title="Health score",
    )
    figure.update_yaxes(range=[0, 105])
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


def _apply_premium_layout(figure: go.Figure, title: str, yaxis_title: str) -> None:
    """Apply premium dark chart styling."""
    figure.update_layout(
        template=PREMIUM_TEMPLATE,
        title={
            "text": title,
            "font": {"size": 20},
        },
        xaxis_title="Time",
        yaxis_title=yaxis_title,
        hovermode="x unified",
        legend_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8, 18, 32, 0.45)",
        margin={"l": 35, "r": 24, "t": 64, "b": 35},
        font={"family": "Inter, Segoe UI, Arial", "color": "#dbeafe"},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
    )
    figure.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.1)",
    )
    figure.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.1)",
    )
