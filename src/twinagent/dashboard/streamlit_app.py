r"""Streamlit dashboard for TwinAgent AI.

Run from the project root:

    streamlit run src\twinagent\dashboard\streamlit_app.py
"""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st  # noqa: E402

from twinagent.agent import TwinAgentCopilot  # noqa: E402
from twinagent.dashboard.charts import (  # noqa: E402
    DEFAULT_SENSOR_COLUMNS,
    create_anomaly_score_chart,
    create_health_score_chart,
    create_sensor_timeseries_chart,
    filter_time_window,
)
from twinagent.dashboard.components import (  # noqa: E402
    DashboardPaths,
    build_incident_summary,
    build_machine_overview,
    incidents_to_dataframe,
    load_incidents,
    load_processed_data,
)


st.set_page_config(
    page_title="TwinAgent AI",
    page_icon="🏭",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def cached_processed_data(path: str):
    """Load processed data with Streamlit caching."""
    return load_processed_data(path)


@st.cache_data(show_spinner=False)
def cached_incidents(path: str):
    """Load incidents with Streamlit caching."""
    return load_incidents(path)


def main() -> None:
    """Render the TwinAgent AI Streamlit dashboard."""
    paths = DashboardPaths(project_root=PROJECT_ROOT)

    st.title("TwinAgent AI")
    st.caption("Agentic Copilot for Industrial Digital Twins")

    st.markdown(
        "This dashboard visualizes a synthetic conveyor-motor digital twin, "
        "anomaly detection output, health scoring, incidents, and grounded "
        "copilot explanations."
    )

    try:
        dataframe = cached_processed_data(str(paths.processed_data_path))
        incidents = cached_incidents(str(paths.incidents_path))
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.info(
            "Run these commands first: "
            r"`python scripts\generate_synthetic_data.py` and "
            r"`python scripts\run_anomaly_detection.py`."
        )
        return

    render_overview(dataframe, incidents)
    render_timeline_section(dataframe)
    render_incident_section(dataframe, incidents)
    render_copilot_section(incidents)


def render_overview(dataframe, incidents) -> None:
    """Render machine overview metrics."""
    st.header("1. Machine overview")
    overview = build_machine_overview(dataframe)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Machine", overview["machine_id"])
    col2.metric("State", overview["machine_state"])
    col3.metric("Latest health", overview["health_score"])
    col4.metric("Risk", overview["risk_level"])
    col5.metric("Incidents", len(incidents))

    col6, col7, col8 = st.columns(3)
    col6.metric("Max anomaly score", overview["max_anomaly_score"])
    col7.metric("Minimum health score", overview["min_health_score"])
    col8.metric("Anomaly rows", f"{overview['anomaly_rows']} / {overview['total_rows']}")

    st.caption(f"Latest timestamp: {overview['latest_timestamp']}")


def render_timeline_section(dataframe) -> None:
    """Render sensor, anomaly, and health timelines."""
    st.header("2. Sensor and health timelines")

    selected_sensors = st.multiselect(
        "Sensors to display",
        options=[sensor for sensor in DEFAULT_SENSOR_COLUMNS if sensor in dataframe.columns],
        default=["temperature_c", "vibration_mm_s", "current_a", "throughput_units_min"],
    )

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.text_input(
            "Start time",
            value=str(dataframe["timestamp"].min()).replace(" ", "T")[:19],
        )
    with col2:
        end_time = st.text_input(
            "End time",
            value=str(dataframe["timestamp"].max()).replace(" ", "T")[:19],
        )

    try:
        filtered = filter_time_window(dataframe, start_time=start_time, end_time=end_time)
    except ValueError as error:
        st.warning(str(error))
        return

    st.plotly_chart(
        create_sensor_timeseries_chart(filtered, sensor_columns=selected_sensors),
        width="stretch",
    )
    st.plotly_chart(create_anomaly_score_chart(filtered), width="stretch")
    st.plotly_chart(create_health_score_chart(filtered), width="stretch")


def render_incident_section(dataframe, incidents) -> None:
    """Render incident list and selected incident details."""
    st.header("3. Incidents")

    incidents_df = incidents_to_dataframe(incidents)
    st.dataframe(incidents_df, width="stretch")

    if not incidents:
        st.info("No incidents were generated.")
        return

    incident_ids = [incident["incident_id"] for incident in incidents]
    selected_id = st.selectbox("Select incident", options=incident_ids)
    selected_incident = next(incident for incident in incidents if incident["incident_id"] == selected_id)
    summary = build_incident_summary(selected_incident)

    st.subheader(f"Incident detail: {selected_id}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Severity", summary["severity"])
    col2.metric("Suspected fault", summary["suspected_fault"])
    col3.metric("Max anomaly score", summary["max_anomaly_score"])

    st.write(f"**Time window:** {summary['time_window']}")
    st.write(f"**Contributing sensors:** {summary['contributing_sensors']}")

    st.write("**Evidence:**")
    for sensor, evidence in summary["evidence"].items():
        st.markdown(f"- `{sensor}`: {evidence}")


def render_copilot_section(incidents) -> None:
    """Render deterministic copilot question-answer section."""
    st.header("4. AI copilot explanation")

    if not incidents:
        st.info("No incident is available for copilot explanation.")
        return

    incident_ids = [incident["incident_id"] for incident in incidents]
    selected_id = st.selectbox("Incident for copilot", options=incident_ids, key="copilot_incident")
    question = st.text_area(
        "Question",
        value="Why did this incident trigger and what should the technician inspect first?",
        height=90,
    )

    if st.button("Generate copilot explanation"):
        with st.spinner("Calling TwinAgent tools and retrieving engineering context..."):
            copilot = TwinAgentCopilot.from_project_root(PROJECT_ROOT)
            answer = copilot.answer_incident_question(
                incident_id=selected_id,
                question=question,
            )
        st.markdown(answer)


if __name__ == "__main__":
    main()
