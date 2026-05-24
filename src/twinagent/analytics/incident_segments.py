"""Incident episode expansion utilities.

The base incident detector groups nearby anomaly rows into broad incidents.
For demos and dashboards, long anomaly windows are easier to inspect when they
are represented as operational episodes.

This module keeps the original detector output grounded, but splits long
medium/high incidents into smaller episodes and renumbers them sequentially.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def expand_incident_episodes(
    incidents: list[dict[str, Any]],
    *,
    id_prefix: str = "INC",
    long_incident_threshold_seconds: int = 420,
    target_segment_seconds: int = 240,
    max_segments_per_incident: int = 6,
) -> list[dict[str, Any]]:
    """Split long incidents into sequential operational episodes.

    The first generated episode is always ``INC-0001`` when ``id_prefix`` is
    ``INC``. This keeps existing report/export workflows stable.
    """
    expanded: list[dict[str, Any]] = []
    next_number = 1

    for original in incidents:
        episodes = _split_one_incident(
            original,
            long_incident_threshold_seconds=long_incident_threshold_seconds,
            target_segment_seconds=target_segment_seconds,
            max_segments_per_incident=max_segments_per_incident,
        )

        for episode in episodes:
            updated = dict(episode)
            updated["incident_id"] = f"{id_prefix}-{next_number:04d}"
            next_number += 1
            expanded.append(updated)

    return expanded


def _split_one_incident(
    incident: dict[str, Any],
    *,
    long_incident_threshold_seconds: int,
    target_segment_seconds: int,
    max_segments_per_incident: int,
) -> list[dict[str, Any]]:
    """Split one incident if it is long enough."""
    duration = int(incident.get("duration_seconds", 0))
    severity = str(incident.get("severity", "none")).lower()

    if severity == "low" or duration <= long_incident_threshold_seconds:
        updated = dict(incident)
        updated["parent_incident_id"] = str(incident.get("incident_id", ""))
        updated["episode_index"] = 1
        updated["episode_count"] = 1
        return [updated]

    segment_count = min(
        max_segments_per_incident,
        max(2, math.ceil(duration / target_segment_seconds)),
    )

    start_time = pd.Timestamp(incident["start_time"])
    end_time = pd.Timestamp(incident["end_time"])
    total_seconds = max(1, int((end_time - start_time).total_seconds()))

    segments: list[dict[str, Any]] = []
    for segment_index in range(segment_count):
        segment_start_seconds = round((segment_index / segment_count) * total_seconds)
        segment_end_seconds = round(((segment_index + 1) / segment_count) * total_seconds)

        segment_start = start_time + pd.Timedelta(seconds=segment_start_seconds)
        segment_end = start_time + pd.Timedelta(seconds=segment_end_seconds)
        if segment_index == segment_count - 1:
            segment_end = end_time

        updated = dict(incident)
        updated["parent_incident_id"] = str(incident.get("incident_id", ""))
        updated["start_time"] = segment_start.strftime("%Y-%m-%dT%H:%M:%S")
        updated["end_time"] = segment_end.strftime("%Y-%m-%dT%H:%M:%S")
        updated["duration_seconds"] = max(1, int((segment_end - segment_start).total_seconds()))
        updated["episode_index"] = segment_index + 1
        updated["episode_count"] = segment_count
        segments.append(updated)

    return segments
