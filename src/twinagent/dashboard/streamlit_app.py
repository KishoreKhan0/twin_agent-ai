r"""Premium Streamlit dashboard for TwinAgent AI.

Run from the project root:

    streamlit run src\twinagent\dashboard\streamlit_app.py
"""

from __future__ import annotations

from html import escape
from pathlib import Path
import re
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
from twinagent.fleet import answer_fleet_question, analyze_fault_patterns  # noqa: E402
from twinagent.maintenance import build_work_order_queue  # noqa: E402
from twinagent.dashboard.fleet_components import (  # noqa: E402
    FleetDashboardPaths,
    build_fleet_overview,
    filter_fleet_machine,
    fleet_artifacts_available,
    fleet_incidents_table,
    fleet_machine_table,
    incidents_for_machine,
    load_fleet_incidents,
    load_fleet_processed_data,
    load_fleet_summary,
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
    initial_sidebar_state="expanded",
)


EXPECTED_FLEET_MACHINE_COUNT = 12
EXPECTED_MIN_FLEET_INCIDENTS = 20
EXPECTED_LOCAL_SENSOR_ROWS = 21600
EXPECTED_MIN_LOCAL_INCIDENTS = 10


@st.cache_data(show_spinner=False)
def cached_processed_data(path: str):
    """Load processed data with Streamlit caching."""
    return load_processed_data(path)


@st.cache_data(show_spinner=False)
def cached_incidents(path: str):
    """Load incidents with Streamlit caching."""
    return load_incidents(path)



@st.cache_data(show_spinner=False)
def cached_fleet_processed_data(path: str):
    """Load fleet processed data with Streamlit caching."""
    return load_fleet_processed_data(path)


@st.cache_data(show_spinner=False)
def cached_fleet_incidents(path: str):
    """Load fleet incidents with Streamlit caching."""
    return load_fleet_incidents(path)


@st.cache_data(show_spinner=False)
def cached_fleet_summary(path: str):
    """Load fleet summary with Streamlit caching."""
    return load_fleet_summary(path)


def get_fleet_summary_for_display() -> dict | None:
    """Return cached fleet summary if available."""
    paths = FleetDashboardPaths(project_root=PROJECT_ROOT)
    if not fleet_artifacts_available(paths):
        return None

    try:
        return cached_fleet_summary(str(paths.summary_path))
    except (FileNotFoundError, ValueError):
        return None


def is_fleet_summary_stale(fleet_summary: dict | None) -> bool:
    """Return True when fleet artifacts are older than the current expanded demo."""
    if not fleet_summary:
        return True

    fleet = fleet_summary.get("fleet", {})
    machine_count = int(fleet.get("machine_count", 0))
    incident_rows = int(fleet.get("incident_rows", 0))
    return (
        machine_count < EXPECTED_FLEET_MACHINE_COUNT
        or incident_rows < EXPECTED_MIN_FLEET_INCIDENTS
    )


def render_fleet_stale_warning(fleet_summary: dict | None) -> None:
    """Warn if the dashboard is reading old fleet artifacts."""
    if not is_fleet_summary_stale(fleet_summary):
        return

    if fleet_summary:
        fleet = fleet_summary.get("fleet", {})
        st.warning(
            "Fleet artifacts look old. Current files show "
            f"{fleet.get('machine_count', 0)} machines and {fleet.get('incident_rows', 0)} incidents. "
            f"The latest generator should produce {EXPECTED_FLEET_MACHINE_COUNT} machines and "
            f"{EXPECTED_MIN_FLEET_INCIDENTS}+ incidents. Run the fleet generator again."
        )
    else:
        st.info("Fleet artifacts are not generated yet.")

    st.code(r"python scripts\generate_fleet_demo_data.py", language="cmd")


def is_local_demo_stale(dataframe, incidents) -> bool:
    """Return True when local artifacts are older than the rich local demo."""
    return len(dataframe) < EXPECTED_LOCAL_SENSOR_ROWS or len(incidents) < EXPECTED_MIN_LOCAL_INCIDENTS


def render_local_stale_warning(dataframe, incidents) -> None:
    """Warn if the dashboard is reading old local demo artifacts."""
    if not is_local_demo_stale(dataframe, incidents):
        return

    st.warning(
        "Local demo artifacts look old. Current local files show "
        f"{len(dataframe)} rows and {len(incidents)} incident(s). "
        f"The rich local demo should produce at least {EXPECTED_LOCAL_SENSOR_ROWS} rows and "
        f"{EXPECTED_MIN_LOCAL_INCIDENTS}+ incidents. Run bootstrap again."
    )
    st.code(r"python scripts\bootstrap_demo_data.py", language="cmd")


def get_local_dataframe_for_display():
    """Return cached local processed data using DashboardPaths."""
    paths = DashboardPaths(project_root=PROJECT_ROOT)
    return cached_processed_data(str(paths.processed_data_path))


def main() -> None:
    """Render the TwinAgent AI Streamlit dashboard."""
    inject_premium_css()
    paths = DashboardPaths(project_root=PROJECT_ROOT)

    try:
        dataframe = cached_processed_data(str(paths.processed_data_path))
        incidents = cached_incidents(str(paths.incidents_path))
    except (FileNotFoundError, ValueError) as error:
        render_missing_data_state(error)
        return

    render_sidebar(dataframe, incidents)
    render_hero(dataframe, incidents)

    overview_tab, timeline_tab, incidents_tab, work_orders_tab, fleet_tab, copilot_tab = st.tabs(
        [
            "🏭 Overview",
            "📈 Sensor Intelligence",
            "🚨 Incidents",
            "🛠️ Work Orders",
            "🏢 Fleet",
            "🤖 Copilot",
        ]
    )

    with overview_tab:
        render_overview(dataframe, incidents)

    with timeline_tab:
        render_timeline_section(dataframe)

    with incidents_tab:
        render_incident_section(incidents)

    with work_orders_tab:
        render_work_orders_section(incidents)

    with fleet_tab:
        render_fleet_section()

    with copilot_tab:
        render_copilot_section(incidents)


def inject_premium_css() -> None:
    """Inject premium dashboard styling."""
    st.markdown(
        """
        <style>
        :root {
            --bg-0: #07111f;
            --bg-1: #0b1728;
            --card: rgba(255, 255, 255, 0.075);
            --card-border: rgba(255, 255, 255, 0.13);
            --text-main: #eef6ff;
            --text-muted: #9fb0c4;
            --blue: #58a6ff;
            --cyan: #35d0ff;
            --green: #50fa7b;
            --amber: #ffca58;
            --red: #ff6b6b;
            --purple: #a78bfa;
        }

        .stApp {
            background:
                radial-gradient(circle at 15% 10%, rgba(88, 166, 255, 0.22), transparent 30%),
                radial-gradient(circle at 85% 0%, rgba(167, 139, 250, 0.20), transparent 28%),
                radial-gradient(circle at 50% 90%, rgba(53, 208, 255, 0.08), transparent 32%),
                linear-gradient(135deg, #07111f 0%, #0b1728 45%, #111827 100%);
            color: var(--text-main);
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(8, 18, 32, 0.98), rgba(15, 23, 42, 0.98));
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
            color: #dbeafe;
        }

        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 4rem;
            max-width: 1500px;
        }

        h1, h2, h3 {
            letter-spacing: -0.035em;
        }

        div[data-testid="stTabs"] button {
            border-radius: 999px;
            padding: 0.6rem 1.1rem;
            font-weight: 700;
        }

        div[data-testid="stTabs"] [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(88,166,255,0.25), rgba(53,208,255,0.18));
            border: 1px solid rgba(88,166,255,0.35);
        }

        .hero {
            position: relative;
            overflow: hidden;
            padding: 2rem 2.1rem;
            border-radius: 28px;
            border: 1px solid rgba(255, 255, 255, 0.14);
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.82), rgba(30, 41, 59, 0.62)),
                radial-gradient(circle at 85% 10%, rgba(53, 208, 255, 0.18), transparent 32%);
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
            margin-bottom: 1.2rem;
        }

        .hero::after {
            content: "";
            position: absolute;
            top: -80px;
            right: -80px;
            width: 220px;
            height: 220px;
            background: rgba(88, 166, 255, 0.22);
            filter: blur(45px);
            border-radius: 999px;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background: rgba(53, 208, 255, 0.12);
            border: 1px solid rgba(53, 208, 255, 0.26);
            color: #bff2ff;
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.8rem;
        }

        .hero-title {
            font-size: clamp(2.1rem, 5vw, 4.2rem);
            line-height: 0.95;
            font-weight: 900;
            margin: 0;
            color: #f8fbff;
        }

        .hero-subtitle {
            margin-top: 0.8rem;
            max-width: 850px;
            font-size: 1.05rem;
            line-height: 1.65;
            color: var(--text-muted);
        }

        .card {
            padding: 1.1rem 1.15rem;
            border-radius: 22px;
            border: 1px solid var(--card-border);
            background:
                linear-gradient(180deg, rgba(255,255,255,0.09), rgba(255,255,255,0.045));
            box-shadow: 0 16px 45px rgba(0, 0, 0, 0.24);
            min-height: 118px;
        }

        .card:hover {
            border-color: rgba(88, 166, 255, 0.35);
            transform: translateY(-1px);
            transition: all 160ms ease;
        }

        .metric-label {
            color: var(--text-muted);
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.4rem;
        }

        .metric-value {
            color: #ffffff;
            font-size: 1.75rem;
            line-height: 1;
            font-weight: 900;
            letter-spacing: -0.04em;
        }

        .metric-note {
            margin-top: 0.55rem;
            color: #b8c7dc;
            font-size: 0.86rem;
            line-height: 1.35;
        }

        .section-card {
            padding: 1.2rem 1.25rem;
            border-radius: 24px;
            border: 1px solid var(--card-border);
            background: rgba(255, 255, 255, 0.055);
            box-shadow: 0 14px 42px rgba(0, 0, 0, 0.22);
            margin: 0.8rem 0 1rem 0;
        }

        .answer-card {
            padding: 1.25rem 1.35rem;
            border-radius: 24px;
            border: 1px solid rgba(88,166,255,0.25);
            background:
                linear-gradient(180deg, rgba(88,166,255,0.12), rgba(255,255,255,0.045));
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.24);
            margin: 0.9rem 0 1rem 0;
        }

        .answer-label {
            color: #93c5fd;
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }

        .answer-text {
            color: #eef6ff;
            font-size: 1.02rem;
            line-height: 1.65;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            font-weight: 800;
            font-size: 0.82rem;
            border: 1px solid rgba(255,255,255,0.15);
        }

        .pill-healthy {
            background: rgba(80, 250, 123, 0.14);
            color: #b9ffd0;
            border-color: rgba(80, 250, 123, 0.28);
        }

        .pill-watch, .pill-medium {
            background: rgba(255, 202, 88, 0.14);
            color: #ffe2a6;
            border-color: rgba(255, 202, 88, 0.28);
        }

        .pill-high, .pill-critical {
            background: rgba(255, 107, 107, 0.15);
            color: #ffd0d0;
            border-color: rgba(255, 107, 107, 0.3);
        }

        .pill-info {
            background: rgba(88, 166, 255, 0.15);
            color: #cfe5ff;
            border-color: rgba(88, 166, 255, 0.30);
        }

        .incident-title {
            font-size: 1.35rem;
            font-weight: 900;
            letter-spacing: -0.03em;
            color: #ffffff;
            margin-bottom: 0.45rem;
        }

        .mono {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
            color: #dbeafe;
        }

        .muted {
            color: var(--text-muted);
        }

        .stDataFrame {
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.09);
        }

        div[data-testid="stMetricValue"] {
            color: #ffffff;
        }

        div[data-testid="stMetricLabel"] {
            color: #b8c7dc;
        }

        .stButton > button {
            border-radius: 999px;
            padding: 0.72rem 1.25rem;
            font-weight: 900;
            border: 1px solid rgba(88,166,255,0.35);
            background: linear-gradient(135deg, #2563eb, #06b6d4);
            color: white;
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.28);
        }

        .stButton > button:hover {
            border-color: rgba(255,255,255,0.55);
            filter: brightness(1.07);
        }

        div[data-testid="stExpander"] {
            border-radius: 18px;
            border: 1px solid rgba(255,255,255,0.13);
            background: rgba(15, 23, 42, 0.48);
        }

        .copilot-native-title {
            padding: 0.95rem 1.05rem;
            border-radius: 22px;
            border: 1px solid rgba(88,166,255,0.22);
            background: rgba(88,166,255,0.10);
            margin: 1rem 0 0.8rem 0;
        }

        .copilot-native-title h3 {
            font-size: 1.22rem !important;
            margin: 0 0 0.25rem 0 !important;
            letter-spacing: -0.025em;
        }

        .copilot-native-title p {
            font-size: 0.94rem !important;
            line-height: 1.5 !important;
            color: #bfd0e6 !important;
            margin: 0 !important;
        }

        .footer-note {
            color: var(--text-muted);
            font-size: 0.83rem;
            margin-top: 1.25rem;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_missing_data_state(error: Exception) -> None:
    """Render a premium missing-data error state."""
    inject_premium_css()
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">⚠️ Setup required</div>
            <h1 class="hero-title">TwinAgent AI dashboard</h1>
            <p class="hero-subtitle">
                The dashboard is ready, but generated data artifacts are missing.
                Run the pipeline commands below and reload this page.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.error(str(error))
    st.code(
        r"""python scripts\generate_synthetic_data.py
python scripts\run_anomaly_detection.py
python scripts\export_to_sqlite.py""",
        language="cmd",
    )


def render_sidebar(dataframe, incidents) -> None:
    """Render sidebar branding and fleet-aware quick facts."""
    fleet_summary = get_fleet_summary_for_display()
    with st.sidebar:
        st.markdown("## 🏭 TwinAgent AI")
        st.caption("Agentic Copilot for Industrial Digital Twins")
        st.divider()

        latest = dataframe.sort_values("timestamp").iloc[-1]
        st.markdown("### Live artifact status")
        if is_local_demo_stale(dataframe, incidents):
            st.warning(f"Local stale: {len(dataframe)} rows, {len(incidents)} incident(s)")
        else:
            st.success(f"Local loaded: {len(dataframe)} rows, {len(incidents)} incidents")

        if fleet_summary:
            fleet = fleet_summary.get("fleet", {})
            if is_fleet_summary_stale(fleet_summary):
                st.warning(
                    f"Fleet stale: {fleet.get('machine_count', 0)} machines, "
                    f"{fleet.get('incident_rows', 0)} incidents"
                )
            else:
                st.success(
                    f"Fleet loaded: {fleet.get('machine_count', 0)} machines, "
                    f"{fleet.get('incident_rows', 0)} incidents"
                )
        else:
            st.warning("Fleet data not generated")

        st.markdown("### Current local machine")
        st.write(f"**Machine:** `{latest['machine_id']}`")
        st.write(f"**Latest state:** `{latest.get('machine_state', 'unknown')}`")
        st.write(f"**Latest health:** `{int(latest['health_score'])}`")
        st.write(f"**Risk level:** `{latest['risk_level']}`")

        st.divider()
        st.markdown("### Quick commands")
        st.code(
            r"""python scripts\bootstrap_demo_data.py
python scripts\generate_fleet_demo_data.py
python scripts\export_global_fleet_analysis.py
python scripts\export_fleet_triage.py
python scripts\launch_dashboard.py""",
            language="cmd",
        )


def render_hero(dataframe, incidents) -> None:
    """Render premium dashboard hero with local and fleet scope."""
    overview = build_machine_overview(dataframe)
    fleet_summary = get_fleet_summary_for_display()
    risk_class = risk_to_class(overview["risk_level"])

    fleet_badge = "Fleet: not generated"
    fleet_incident_badge = "Fleet incidents: not generated"
    if fleet_summary:
        fleet = fleet_summary.get("fleet", {})
        fleet_badge = f"Fleet: {fleet.get('machine_count', 0)} machines"
        fleet_incident_badge = f"Fleet incidents: {fleet.get('incident_rows', 0)}"
        if is_fleet_summary_stale(fleet_summary):
            fleet_incident_badge += " • stale"

    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">⚡ Industrial AI MVP • Local + Fleet Digital Twin</div>
            <h1 class="hero-title">TwinAgent AI</h1>
            <p class="hero-subtitle">
                Premium monitoring workspace for simulated conveyor-motor digital twins:
                anomaly detection, health scoring, engineering-document retrieval,
                incident explanations, fleet triage, and maintenance recommendations.
            </p>
            <div style="margin-top: 1rem;">
                <span class="status-pill pill-info">Local machine: {escape(overview["machine_id"])}</span>
                <span class="status-pill {risk_class}" style="margin-left: 0.45rem;">
                    Local risk: {escape(overview["risk_level"])}
                </span>
                <span class="status-pill pill-info" style="margin-left: 0.45rem;">
                    Local: {len(dataframe)} rows / {len(incidents)} incidents
                </span>
                <span class="status-pill pill-info" style="margin-left: 0.45rem;">
                    {escape(fleet_badge)}
                </span>
                <span class="status-pill pill-info" style="margin-left: 0.45rem;">
                    {escape(fleet_incident_badge)}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview(dataframe, incidents) -> None:
    """Render premium local and fleet overview."""
    st.markdown("## Executive machine overview")
    render_local_stale_warning(dataframe, incidents)
    overview = build_machine_overview(dataframe)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Local health score", overview["health_score"], "Latest local machine health index")
    with col2:
        metric_card("Local risk level", overview["risk_level"], "Current local operational risk")
    with col3:
        metric_card("Local max anomaly", overview["max_anomaly_score"], "Highest score in current run")
    with col4:
        metric_card("Local incidents", len(incidents), "Single-machine generated events")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        metric_card("Machine state", overview["machine_state"], "Latest detected state")
    with col6:
        metric_card("Min health", overview["min_health_score"], "Worst health score in run")
    with col7:
        metric_card(
            "Anomaly rows",
            overview["anomaly_rows"],
            f"Out of {overview['total_rows']} local rows",
        )
    with col8:
        metric_card("Last update", overview["latest_timestamp"], "Latest local sensor timestamp")

    fleet_summary = get_fleet_summary_for_display()
    st.markdown("## Fleet operations overview")
    render_fleet_stale_warning(fleet_summary)

    if fleet_summary:
        fleet_overview = build_fleet_overview(fleet_summary)
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        with fcol1:
            metric_card("Fleet machines", fleet_overview["machine_count"], "Assets in fleet dataset")
        with fcol2:
            metric_card("Fleet incidents", fleet_overview["incident_rows"], "Fleet-wide maintenance events")
        with fcol3:
            metric_card("High incidents", fleet_overview["high_incidents"], "High-severity fleet events")
        with fcol4:
            metric_card("Sensor rows", fleet_overview["sensor_rows"], "Fleet processed readings")

        fcol5, fcol6 = st.columns(2)
        with fcol5:
            metric_card(
                "Top incident machine",
                fleet_overview["busiest_machine_id"],
                f"{fleet_overview['busiest_machine_incidents']} incidents",
            )
        with fcol6:
            metric_card(
                "Worst min health",
                fleet_overview["worst_machine_min_health"],
                f"Machine: {fleet_overview['worst_machine_id']}",
            )

    local_work_orders = build_work_order_queue(incidents)
    st.markdown("## Maintenance queue overview")
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    with qcol1:
        metric_card("Local work orders", local_work_orders.total_work_orders, "Open maintenance jobs")
    with qcol2:
        metric_card("Local P1 jobs", local_work_orders.open_p1_count, "Urgent local work orders")
    with qcol3:
        metric_card("Local P2 jobs", local_work_orders.open_p2_count, "24-hour local work orders")
    with qcol4:
        metric_card(
            "Priority machine",
            local_work_orders.top_priority_machine or "none",
            "Highest local maintenance pressure",
        )

    st.markdown(
        """
        <div class="section-card">
            <div class="incident-title">MVP status</div>
            <p class="muted">
                This dashboard is backed by synthetic digital-twin data, SQLite persistence,
                local RAG retrieval, deterministic agent tools, fleet triage, FastAPI endpoints,
                and Docker Compose support. Metrics and maintenance outputs are prototype
                signals, not certified production maintenance decisions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_timeline_section(dataframe) -> None:
    """Render premium sensor, anomaly, and health timelines."""
    st.markdown("## Sensor intelligence")

    with st.container(border=True):
        selected_sensors = st.multiselect(
            "Select sensors",
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

    chart_a, chart_b = st.columns([1.15, 0.85])
    with chart_a:
        st.plotly_chart(
            create_sensor_timeseries_chart(filtered, sensor_columns=selected_sensors),
            width="stretch",
            key="single_machine_sensor_timeseries_chart",
        )
    with chart_b:
        st.plotly_chart(
            create_health_score_chart(filtered),
            width="stretch",
            key="single_machine_health_score_chart",
        )

    st.plotly_chart(
        create_anomaly_score_chart(filtered),
        width="stretch",
        key="single_machine_anomaly_score_chart",
    )


def render_incident_section(incidents) -> None:
    """Render single-machine and fleet-wide incident tables."""
    st.markdown("## Incident command center")
    st.caption(
        "Review local demo incidents and fleet-wide incidents. Use the Copilot tab for questions."
    )

    local_tab, fleet_tab = st.tabs(["Single-machine incidents", "Fleet incidents"])

    with local_tab:
        render_local_stale_warning(dataframe=get_local_dataframe_for_display(), incidents=incidents)
        incidents_df = incidents_to_dataframe(incidents)
        st.dataframe(incidents_df, width="stretch", hide_index=True)

        if not incidents:
            st.info("No single-machine incidents were generated.")
        else:
            incident_ids = [incident["incident_id"] for incident in incidents]
            selected_id = st.selectbox(
                "Select local incident for inspection",
                options=incident_ids,
                key="local_incident_selector",
            )
            selected_incident = next(incident for incident in incidents if incident["incident_id"] == selected_id)
            summary = build_incident_summary(selected_incident)

            severity_class = risk_to_class(summary["severity"])

            st.markdown(
                f"""
                <div class="section-card">
                    <div class="incident-title">Incident {escape(selected_id)}</div>
                    <span class="status-pill {severity_class}">Severity: {escape(str(summary["severity"]))}</span>
                    <span class="status-pill pill-info" style="margin-left: 0.45rem;">
                        Fault: {escape(str(summary["suspected_fault"]))}
                    </span>
                    <span class="status-pill pill-info" style="margin-left: 0.45rem;">
                        Max anomaly: {escape(str(summary["max_anomaly_score"]))}
                    </span>
                    <p class="muted" style="margin-top: 1rem;">
                        <strong>Time window:</strong>
                        <span class="mono">{escape(str(summary["time_window"]))}</span>
                    </p>
                    <p class="muted">
                        <strong>Contributing sensors:</strong>
                        {escape(str(summary["contributing_sensors"]))}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("### Detector evidence")
            evidence_cols = st.columns(max(1, min(4, len(summary["evidence"]) or 1)))
            for index, (sensor, evidence) in enumerate(summary["evidence"].items()):
                with evidence_cols[index % len(evidence_cols)]:
                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="metric-label">{escape(sensor)}</div>
                            <div class="metric-note">{escape(str(evidence))}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with fleet_tab:
        paths = FleetDashboardPaths(project_root=PROJECT_ROOT)
        if not fleet_artifacts_available(paths):
            st.info(
                "Fleet incidents are not available yet. Run "
                "`python scripts\\generate_fleet_demo_data.py`."
            )
            st.code(r"python scripts\generate_fleet_demo_data.py", language="cmd")
            return

        try:
            fleet_incidents = cached_fleet_incidents(str(paths.incidents_path))
            fleet_summary = cached_fleet_summary(str(paths.summary_path))
        except (FileNotFoundError, ValueError) as error:
            st.warning(str(error))
            return

        render_fleet_stale_warning(fleet_summary)
        fleet_overview = build_fleet_overview(fleet_summary)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Fleet incidents", fleet_overview["incident_rows"], "All generated fleet events")
        with col2:
            metric_card("High incidents", fleet_overview["high_incidents"], "High-severity fleet events")
        with col3:
            metric_card("Top machine", fleet_overview["busiest_machine_id"], "Most incident activity")
        with col4:
            metric_card("Worst min health", fleet_overview["worst_machine_min_health"], fleet_overview["worst_machine_id"])

        incidents_table = fleet_incidents_table(fleet_incidents)

        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            machine_filter = st.multiselect(
                "Filter by machine",
                options=sorted(incidents_table["machine_id"].unique()),
                default=[],
                key="fleet_incident_machine_filter",
            )
        with filter_col2:
            severity_filter = st.multiselect(
                "Filter by severity",
                options=sorted(incidents_table["severity"].unique()),
                default=[],
                key="fleet_incident_severity_filter",
            )
        with filter_col3:
            fault_filter = st.multiselect(
                "Filter by fault",
                options=sorted(incidents_table["suspected_fault"].unique()),
                default=[],
                key="fleet_incident_fault_filter",
            )

        filtered_incidents = incidents_table.copy()
        if machine_filter:
            filtered_incidents = filtered_incidents[filtered_incidents["machine_id"].isin(machine_filter)]
        if severity_filter:
            filtered_incidents = filtered_incidents[filtered_incidents["severity"].isin(severity_filter)]
        if fault_filter:
            filtered_incidents = filtered_incidents[filtered_incidents["suspected_fault"].isin(fault_filter)]

        st.dataframe(filtered_incidents, width="stretch", hide_index=True)

        st.caption(
            "Ask comparison questions in the Copilot tab, for example: "
            "`Compare bearing wear incidents` or `Which machine should maintenance inspect first?`"
        )



def render_work_orders_section(incidents) -> None:
    """Render local and fleet maintenance work-order queues."""
    st.markdown("## Maintenance work-order queue")
    st.caption(
        "Convert incident analytics into technician-ready maintenance jobs with priorities, due windows, and checklists."
    )

    local_tab, fleet_tab = st.tabs(["Local work orders", "Fleet work orders"])

    with local_tab:
        if not incidents:
            st.info("No local incidents are available for work-order generation.")
        else:
            local_queue = build_work_order_queue(incidents, work_order_prefix="LWO")
            render_work_order_queue(local_queue, key_prefix="local_work_orders")

    with fleet_tab:
        paths = FleetDashboardPaths(project_root=PROJECT_ROOT)
        if not fleet_artifacts_available(paths):
            st.info("Fleet incidents are not available yet. Run the fleet generator.")
            st.code(r"python scripts\generate_fleet_demo_data.py", language="cmd")
            return

        try:
            fleet_summary = cached_fleet_summary(str(paths.summary_path))
            fleet_incidents = cached_fleet_incidents(str(paths.incidents_path))
        except (FileNotFoundError, ValueError) as error:
            st.warning(str(error))
            return

        render_fleet_stale_warning(fleet_summary)
        fleet_queue = build_work_order_queue(fleet_incidents, work_order_prefix="FWO")
        render_work_order_queue(fleet_queue, key_prefix="fleet_work_orders")


def render_work_order_queue(queue, *, key_prefix: str) -> None:
    """Render a work-order queue."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Open work orders", queue.total_work_orders, "Generated from incidents")
    with col2:
        metric_card("P1 urgent", queue.open_p1_count, "Due within 4 hours")
    with col3:
        metric_card("P2 priority", queue.open_p2_count, "Due within 24 hours")
    with col4:
        metric_card("Machines affected", queue.machines_affected, f"Top: {queue.top_priority_machine or 'none'}")

    rows = []
    for order in queue.work_orders:
        rows.append(
            {
                "work_order_id": order.work_order_id,
                "incident_id": order.source_incident_id,
                "machine_id": order.machine_id,
                "priority": order.priority,
                "severity": order.severity,
                "fault": order.suspected_fault,
                "status": order.status,
                "due_within_hours": order.due_within_hours,
                "effort_min": order.estimated_effort_minutes,
                "recommended_action": order.recommended_action,
            }
        )

    if not rows:
        st.info("No work orders to display.")
        return

    st.dataframe(rows, width="stretch", hide_index=True)

    order_ids = [order.work_order_id for order in queue.work_orders]
    selected_id = st.selectbox(
        "Select work order for technician checklist",
        options=order_ids,
        key=f"{key_prefix}_selected_order",
    )
    selected_order = next(order for order in queue.work_orders if order.work_order_id == selected_id)

    st.markdown(
        f"""
        <div class="section-card">
            <div class="incident-title">{escape(selected_order.work_order_id)} • {escape(selected_order.machine_id)}</div>
            <span class="status-pill pill-info">Priority: {escape(selected_order.priority)}</span>
            <span class="status-pill pill-info" style="margin-left: 0.45rem;">
                Fault: {escape(selected_order.suspected_fault)}
            </span>
            <span class="status-pill pill-info" style="margin-left: 0.45rem;">
                Due: {selected_order.due_within_hours}h
            </span>
            <p class="muted" style="margin-top: 1rem;">
                <strong>Recommended action:</strong> {escape(selected_order.recommended_action)}
            </p>
            <p class="muted">
                <strong>Evidence:</strong> {escape(selected_order.evidence_summary)}
            </p>
            <p class="muted">
                <strong>Safety:</strong> {escape(selected_order.safety_note)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Technician checklist")
    for item in selected_order.inspection_checklist:
        st.checkbox(item, key=f"{key_prefix}_{selected_order.work_order_id}_{item}")


def render_fleet_section() -> None:
    """Render optional fleet-level dashboard section."""
    st.markdown("## Fleet command center")

    paths = FleetDashboardPaths(project_root=PROJECT_ROOT)
    if not fleet_artifacts_available(paths):
        st.info(
            "Fleet demo artifacts are not available yet. Run "
            "`python scripts\\generate_fleet_demo_data.py` from the project root."
        )
        st.code(r"python scripts\generate_fleet_demo_data.py", language="cmd")
        return

    try:
        fleet_data = cached_fleet_processed_data(str(paths.processed_data_path))
        fleet_incidents = cached_fleet_incidents(str(paths.incidents_path))
        fleet_summary = cached_fleet_summary(str(paths.summary_path))
    except (FileNotFoundError, ValueError) as error:
        st.warning(str(error))
        return

    render_fleet_stale_warning(fleet_summary)
    overview = build_fleet_overview(fleet_summary)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Fleet machines", overview["machine_count"], "Assets in fleet demo")
    with col2:
        metric_card("Sensor rows", overview["sensor_rows"], "Fleet processed readings")
    with col3:
        metric_card("Incidents", overview["incident_rows"], "Fleet maintenance events")
    with col4:
        metric_card("High incidents", overview["high_incidents"], "High-severity events")

    col5, col6 = st.columns(2)
    with col5:
        metric_card(
            "Worst min health",
            overview["worst_machine_min_health"],
            f"Machine: {overview['worst_machine_id']}",
        )
    with col6:
        metric_card(
            "Most incidents",
            overview["busiest_machine_incidents"],
            f"Machine: {overview['busiest_machine_id']}",
        )

    st.markdown(
        f"""
        <div class="section-card">
            <div class="incident-title">Fleet time range</div>
            <p class="muted">
                <span class="mono">{escape(str(overview["time_start"]))}</span>
                →
                <span class="mono">{escape(str(overview["time_end"]))}</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Machine health table")
    machine_table = fleet_machine_table(fleet_summary)
    st.dataframe(machine_table, width="stretch", hide_index=True)

    st.markdown("### Fleet incidents")
    incidents_table = fleet_incidents_table(fleet_incidents)
    st.dataframe(incidents_table, width="stretch", hide_index=True)

    st.markdown("### Machine drill-down")
    machine_ids = list(machine_table["machine_id"])
    selected_machine = st.selectbox(
        "Select fleet machine",
        options=machine_ids,
        key="fleet_machine_selector",
    )

    machine_frame = filter_fleet_machine(fleet_data, selected_machine)
    machine_incidents = incidents_for_machine(fleet_incidents, selected_machine)

    drill_col1, drill_col2 = st.columns([1.2, 0.8])
    with drill_col1:
        selected_sensors = [
            sensor
            for sensor in ["temperature_c", "vibration_mm_s", "current_a", "throughput_units_min"]
            if sensor in machine_frame.columns
        ]
        st.plotly_chart(
            create_sensor_timeseries_chart(machine_frame, sensor_columns=selected_sensors),
            width="stretch",
            key=f"fleet_sensor_timeseries_chart_{selected_machine}",
        )

    with drill_col2:
        st.plotly_chart(
            create_health_score_chart(machine_frame),
            width="stretch",
            key=f"fleet_health_score_chart_{selected_machine}",
        )

    st.plotly_chart(
        create_anomaly_score_chart(machine_frame),
        width="stretch",
        key=f"fleet_anomaly_score_chart_{selected_machine}",
    )

    if machine_incidents:
        st.markdown(f"### Incidents for `{selected_machine}`")
        st.dataframe(fleet_incidents_table(machine_incidents), width="stretch", hide_index=True)
    else:
        st.success(f"No incidents found for `{selected_machine}`.")




def render_copilot_section(incidents) -> None:
    """Render one global copilot workspace for fleet and targeted incident questions."""
    st.markdown("## AI copilot workspace")
    st.caption(
        "Global fleet mode is the default. Specific-incident mode is available only when needed."
    )

    fleet_summary = get_fleet_summary_for_display()
    fleet_available = fleet_summary is not None

    mode_labels = {
        "Deterministic (free/local)": "deterministic",
        "Auto (AI if configured, otherwise local)": "auto",
        "AI-assisted (OpenAI API)": "ai",
    }

    quick_prompts = [
        "Which machine should maintenance inspect first?",
        "Compare bearing wear incidents.",
        "Show current anomaly incidents.",
        "Why is line1_motor2 critical?",
        "Which issue appears most often?",
        "Show the fleet incident timeline.",
        "What should maintenance inspect first?",
    ]

    col_main, col_side = st.columns([2.45, 0.9])

    with col_side:
        st.markdown("### Quick prompts")
        st.caption("Copy one into the question box.")
        for prompt in quick_prompts:
            st.code(prompt, language=None)

        st.markdown("### Available data")
        if fleet_available and fleet_summary:
            fleet = fleet_summary.get("fleet", {})
            if is_fleet_summary_stale(fleet_summary):
                st.warning(
                    f"Fleet stale: {fleet.get('machine_count', 0)} machines, "
                    f"{fleet.get('incident_rows', 0)} incidents"
                )
            else:
                st.success(
                    f"Fleet: {fleet.get('machine_count', 0)} machines, "
                    f"{fleet.get('incident_rows', 0)} incidents"
                )
        else:
            st.warning("Fleet data missing")
            st.code(r"python scripts\generate_fleet_demo_data.py", language="cmd")

        local_frame = get_local_dataframe_for_display()
        if is_local_demo_stale(local_frame, incidents):
            st.warning(f"Local stale: {len(local_frame)} rows, {len(incidents)} incident(s)")
        else:
            st.info(f"Local: {len(local_frame)} rows, {len(incidents)} incidents")

    with col_main:
        render_fleet_stale_warning(fleet_summary)

        with st.container(border=True):
            selected_scope = st.radio(
                "Question scope",
                options=["Global fleet", "Specific incident"],
                index=0,
                horizontal=True,
                key="copilot_scope_v5",
                help=(
                    "Global fleet answers across all fleet machines/incidents. "
                    "Specific incident shows the single-incident workflow only when selected."
                ),
            )

            selected_mode = "deterministic"
            if selected_scope == "Specific incident":
                mode_label = st.selectbox(
                    "Copilot mode",
                    options=list(mode_labels.keys()),
                    index=0,
                    key="specific_incident_copilot_mode_v3",
                    help=(
                        "Deterministic is free/offline. AI-assisted requires OpenAI API billing and "
                        "OPENAI_API_KEY. Auto uses AI only when configured."
                    ),
                )
                selected_mode = mode_labels[mode_label]
            else:
                st.caption("Mode: deterministic fleet analysis across all fleet incidents.")

            selected_id = None
            if selected_scope == "Specific incident":
                if incidents:
                    incident_ids = [incident["incident_id"] for incident in incidents]
                    selected_id = st.selectbox(
                        "Incident for targeted question",
                        options=incident_ids,
                        key="copilot_specific_incident_selector_v3",
                    )
                else:
                    st.warning("No local incident is available.")

            default_question = (
                "Which machine should maintenance inspect first?"
                if selected_scope == "Global fleet"
                else "Why did this incident trigger and what should the technician inspect first?"
            )

            question = st.text_area(
                "Question",
                value=default_question,
                height=120,
                placeholder=(
                    "Examples: compare bearing wear incidents, which machine is worst, "
                    "show current anomaly incidents, why is line1_motor2 critical?"
                ),
                key=f"copilot_question_v5_{selected_scope}",
            )

            generate = st.button("Ask TwinAgent copilot", type="primary", key="ask_twinagent_copilot_v5")

        if not generate:
            return

        if selected_scope == "Global fleet":
            if not fleet_available or not fleet_summary:
                st.error(
                    "Fleet data is not available. Run "
                    "`python scripts\\generate_fleet_demo_data.py` first."
                )
                return

            answer = answer_fleet_question(fleet_summary, question)
            remember_dashboard_answer(
                question=question,
                answer=answer.answer,
                incident_id="GLOBAL_FLEET",
                mode="deterministic_fleet",
                metadata={
                    "intent": answer.intent,
                    "provider": "deterministic_fleet",
                    "suggested_followups": answer.suggested_followups,
                },
            )

            st.markdown(
                f"""
                <div class="section-card">
                    <div class="incident-title">Global fleet copilot response</div>
                    <p class="muted">
                        Scope: <strong>global fleet</strong>. Intent:
                        <strong>{escape(answer.intent)}</strong>. Answered across all fleet machines/incidents.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="answer-card">
                    <div class="answer-label">Global fleet answer</div>
                    <div class="answer-text">{escape(answer.answer)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if answer.evidence:
                with st.expander("Evidence used", expanded=False):
                    for item in answer.evidence:
                        st.markdown(f"- {item}")

            render_followups(answer.suggested_followups)
            render_answer_history()
            return

        if selected_scope == "Specific incident":
            if not selected_id:
                st.error("Select an incident for targeted incident mode.")
                return

            with st.spinner("Calling TwinAgent tools and selected copilot mode..."):
                copilot = TwinAgentCopilot.from_project_root(PROJECT_ROOT)
                try:
                    if hasattr(copilot, "answer_incident_question_with_metadata"):
                        result = copilot.answer_incident_question_with_metadata(
                            incident_id=selected_id,
                            question=question,
                            copilot_mode=selected_mode,
                        )
                        answer = result.answer
                        metadata = result.to_dict()
                    else:
                        answer = copilot.answer_incident_question(
                            incident_id=selected_id,
                            question=question,
                            copilot_mode=selected_mode,
                        )
                        metadata = {
                            "intent": "unknown",
                            "provider": "unknown",
                            "suggested_followups": [],
                        }
                except TypeError as error:
                    if "copilot_mode" not in str(error):
                        raise
                    answer = copilot.answer_incident_question(
                        incident_id=selected_id,
                        question=question,
                    )
                    metadata = {
                        "intent": "legacy_backend",
                        "provider": "legacy",
                        "suggested_followups": [],
                    }

            remember_dashboard_answer(
                question=question,
                answer=answer,
                incident_id=selected_id,
                mode=selected_mode,
                metadata=metadata,
            )

            st.markdown(
                f"""
                <div class="section-card">
                    <div class="incident-title">Targeted incident copilot response</div>
                    <p class="muted">
                        Scope: <strong>specific incident</strong>. Incident:
                        <strong>{escape(selected_id)}</strong>. Intent:
                        <strong>{escape(str(metadata.get("intent", "unknown")))}</strong>.
                        Provider: <strong>{escape(str(metadata.get("provider", "unknown")))}</strong>.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_copilot_answer_native(answer)
            render_followups(metadata.get("suggested_followups", []))
            render_answer_history()


def remember_dashboard_answer(
    question: str,
    answer: str,
    incident_id: str,
    mode: str,
    metadata: dict,
) -> None:
    """Store recent answers in Streamlit session state."""
    history = st.session_state.setdefault("copilot_answer_history", [])
    history.insert(
        0,
        {
            "question": question,
            "answer": clean_copilot_answer_for_display(answer),
            "incident_id": incident_id,
            "mode": mode,
            "intent": metadata.get("intent", "unknown"),
            "provider": metadata.get("provider", "unknown"),
        },
    )
    del history[5:]


def render_followups(followups: list[str]) -> None:
    """Render suggested follow-up questions."""
    if not followups:
        return

    st.markdown("### Suggested follow-up questions")
    cols = st.columns(min(3, len(followups)))
    for index, followup in enumerate(followups[:3]):
        with cols[index % len(cols)]:
            st.info(followup)


def render_answer_history() -> None:
    """Render recent dashboard answer history."""
    history = st.session_state.get("copilot_answer_history", [])
    if len(history) <= 1:
        return

    with st.expander("Recent copilot answers", expanded=False):
        for item in history[1:]:
            st.markdown(
                f"**{item['question']}**  \n"
                f"Scope `{item['incident_id']}` • Mode `{item['mode']}` • Intent `{item['intent']}`"
            )
            st.caption(item["answer"][:350])
            st.divider()



def render_copilot_answer_native(answer: str) -> None:
    """Render copilot answers, including short/freeform answers and full reports."""
    answer = clean_copilot_answer_for_display(answer)
    question, sections = parse_copilot_answer(answer)

    st.markdown(
        """
        <div class="copilot-native-title">
            <h3>Grounded incident explanation</h3>
            <p>TwinAgent AI Copilot • Evidence-based maintenance reasoning</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if question:
        st.info(f"Question: {strip_markdown(question)}")

    if not sections:
        render_short_answer(answer)
        return

    for index, (title, body_lines) in enumerate(sections, start=1):
        with st.container(border=True):
            st.markdown(f"**{index}. {strip_markdown(title)}**")
            render_copilot_body_lines(body_lines)



def clean_copilot_answer_for_display(answer: str) -> str:
    """Remove provider failure/debug text from user-facing dashboard output."""
    if not answer:
        return ""

    # Remove the old fallback suffix that was previously appended by the backend.
    patterns = [
        r"\n*_?AI provider failed, so this answer used deterministic fallback:.*",
        r"\n*_?AI provider failed.*",
        r"\n*RetryError\[.*",
        r"\n*state=finished raised .*",
    ]

    cleaned = answer
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)

    # Defensive cleanup for any unmatched raw exception fragments.
    blocked_fragments = [
        "RateLimitError",
        "RetryError",
        "Future at",
        "state=finished raised",
        "OpenAIError",
        "APIStatusError",
    ]

    lines = []
    for line in cleaned.splitlines():
        if any(fragment in line for fragment in blocked_fragments):
            continue
        lines.append(line)

    return "\n".join(lines).strip()


def render_short_answer(answer: str) -> None:
    """Render a focused short/freeform copilot answer."""
    cleaned_answer = strip_markdown(clean_copilot_answer_for_display(answer))
    if not cleaned_answer:
        st.warning("No answer was generated for this question.")
        return

    st.markdown(
        f"""
        <div class="answer-card">
            <div class="answer-label">Focused answer</div>
            <div class="answer-text">{escape(cleaned_answer)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_copilot_body_lines(body_lines: list[str]) -> None:
    """Render parsed copilot section lines in a consistent native style."""
    pending_bullets: list[str] = []
    source_title: str | None = None
    source_citation: str | None = None

    def flush_bullets() -> None:
        if pending_bullets:
            st.markdown("\n".join(f"- {bullet}" for bullet in pending_bullets))
            pending_bullets.clear()

    def flush_source_card() -> None:
        nonlocal source_title, source_citation
        if source_title:
            with st.expander(source_title, expanded=False):
                if source_citation:
                    st.caption(source_citation)
            source_title = None
            source_citation = None

    for raw_line in body_lines:
        line = raw_line.strip()
        if not line:
            continue

        source_match = re.match(r"^(\d+)\.\s+\*\*(.+?)\*\*\s+`?\[(.+?)\]`?$", line)
        if source_match:
            flush_bullets()
            flush_source_card()
            source_title = f"{source_match.group(1)}. {strip_markdown(source_match.group(2))}"
            source_citation = source_match.group(3)
            continue

        if source_title and not line.startswith("- "):
            with st.expander(source_title, expanded=False):
                if source_citation:
                    st.caption(source_citation)
                st.write(strip_markdown(line))
            source_title = None
            source_citation = None
            continue

        if line.startswith("- "):
            flush_source_card()
            pending_bullets.append(strip_markdown(line[2:].strip()))
            continue

        if re.match(r"^\d+\.\s+", line):
            flush_source_card()
            pending_bullets.append(strip_markdown(re.sub(r"^\d+\.\s+", "", line)))
            continue

        flush_bullets()
        flush_source_card()

        if line == "Incident-level evidence from the detector:":
            st.markdown("**Incident-level evidence from the detector:**")
        elif line == "TwinAgent AI response policy:":
            st.markdown("**TwinAgent AI response policy:**")
        else:
            st.write(strip_markdown(line))

    flush_bullets()
    flush_source_card()


def parse_copilot_answer(answer: str) -> tuple[str, list[tuple[str, list[str]]]]:
    """Parse the deterministic copilot answer into a question and sections."""
    question = ""
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for raw_line in answer.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("# "):
            continue

        if line.startswith("**Question:**"):
            question = line.replace("**Question:**", "", 1).strip()
            continue

        heading_match = re.match(r"^##\s+(?:\d+\.\s*)?(.+)$", line)
        if heading_match:
            if current_title is not None:
                sections.append((current_title, current_lines))
            current_title = heading_match.group(1).strip()
            current_lines = []
            continue

        if current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections.append((current_title, current_lines))

    return question, sections


def strip_markdown(text: str) -> str:
    """Remove simple Markdown formatting while preserving readable text."""
    cleaned = text.strip()
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = cleaned.replace("## ", "")
    return cleaned


def metric_card(label: str, value: object, note: str) -> None:
    """Render a custom metric card."""
    st.markdown(
        f"""
        <div class="card">
            <div class="metric-label">{escape(str(label))}</div>
            <div class="metric-value">{escape(str(value))}</div>
            <div class="metric-note">{escape(str(note))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_to_class(value: object) -> str:
    """Map a risk/severity value to a CSS class."""
    normalized = str(value).lower()
    if normalized in {"healthy", "normal", "low"}:
        return "pill-healthy"
    if normalized in {"watch", "medium", "degraded", "warning"}:
        return "pill-medium"
    if normalized in {"high", "critical"}:
        return "pill-critical"
    return "pill-info"


if __name__ == "__main__":
    main()
