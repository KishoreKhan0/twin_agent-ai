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

    overview_tab, timeline_tab, incidents_tab, copilot_tab = st.tabs(
        [
            "🏭 Overview",
            "📈 Sensor Intelligence",
            "🚨 Incidents",
            "🤖 Copilot",
        ]
    )

    with overview_tab:
        render_overview(dataframe, incidents)

    with timeline_tab:
        render_timeline_section(dataframe)

    with incidents_tab:
        render_incident_section(incidents)

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

        /* Native copilot renderer: consistent font sizes without raw HTML cards. */
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

        .copilot-section-label {
            font-size: 1.02rem;
            font-weight: 900;
            color: #ffffff;
            margin: 0.2rem 0 0.45rem 0;
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
    """Render sidebar branding and quick facts."""
    with st.sidebar:
        st.markdown("## 🏭 TwinAgent AI")
        st.caption("Agentic Copilot for Industrial Digital Twins")
        st.divider()

        latest = dataframe.sort_values("timestamp").iloc[-1]
        st.markdown("### Live artifact status")
        st.success("Processed data loaded")
        st.success(f"{len(incidents)} incident(s) loaded")

        st.markdown("### Current machine")
        st.write(f"**Machine:** `{latest['machine_id']}`")
        st.write(f"**Latest state:** `{latest.get('machine_state', 'unknown')}`")
        st.write(f"**Latest health:** `{int(latest['health_score'])}`")
        st.write(f"**Risk level:** `{latest['risk_level']}`")

        st.divider()
        st.markdown("### Quick commands")
        st.code(
            r"""python scripts\bootstrap_demo_data.py
python scripts\launch_dashboard.py
python scripts\launch_api.py""",
            language="cmd",
        )


def render_hero(dataframe, incidents) -> None:
    """Render premium dashboard hero."""
    overview = build_machine_overview(dataframe)
    risk_class = risk_to_class(overview["risk_level"])

    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">⚡ Industrial AI MVP • Local Digital Twin</div>
            <h1 class="hero-title">TwinAgent AI</h1>
            <p class="hero-subtitle">
                Premium monitoring workspace for a simulated conveyor-motor digital twin:
                anomaly detection, health scoring, engineering-document retrieval,
                incident explanations, and maintenance recommendations.
            </p>
            <div style="margin-top: 1rem;">
                <span class="status-pill pill-info">Machine: {escape(overview["machine_id"])}</span>
                <span class="status-pill {risk_class}" style="margin-left: 0.45rem;">
                    Risk: {escape(overview["risk_level"])}
                </span>
                <span class="status-pill pill-info" style="margin-left: 0.45rem;">
                    Incidents: {len(incidents)}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview(dataframe, incidents) -> None:
    """Render premium machine overview."""
    st.markdown("## Executive machine overview")
    overview = build_machine_overview(dataframe)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Health score", overview["health_score"], "Latest machine health index")
    with col2:
        metric_card("Risk level", overview["risk_level"], "Current operational risk")
    with col3:
        metric_card("Max anomaly", overview["max_anomaly_score"], "Highest score in current run")
    with col4:
        metric_card("Incidents", len(incidents), "Generated maintenance events")

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        metric_card("Machine state", overview["machine_state"], "Latest detected state")
    with col6:
        metric_card("Min health", overview["min_health_score"], "Worst health score in run")
    with col7:
        metric_card(
            "Anomaly rows",
            overview["anomaly_rows"],
            f"Out of {overview['total_rows']} total rows",
        )
    with col8:
        metric_card("Last update", overview["latest_timestamp"], "Latest sensor timestamp")

    st.markdown(
        """
        <div class="section-card">
            <div class="incident-title">MVP status</div>
            <p class="muted">
                This dashboard is backed by synthetic digital-twin data, SQLite persistence,
                local RAG retrieval, deterministic agent tools, FastAPI endpoints, and Docker
                Compose support. Metrics and maintenance outputs are prototype signals, not
                certified production maintenance decisions.
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
        )
    with chart_b:
        st.plotly_chart(create_health_score_chart(filtered), width="stretch")

    st.plotly_chart(create_anomaly_score_chart(filtered), width="stretch")


def render_incident_section(incidents) -> None:
    """Render premium incident list and selected incident details."""
    st.markdown("## Incident command center")

    incidents_df = incidents_to_dataframe(incidents)
    st.dataframe(incidents_df, width="stretch", hide_index=True)

    if not incidents:
        st.info("No incidents were generated.")
        return

    incident_ids = [incident["incident_id"] for incident in incidents]
    selected_id = st.selectbox("Select incident", options=incident_ids)
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


def render_copilot_section(incidents) -> None:
    """Render premium deterministic copilot question-answer section."""
    st.markdown("## AI copilot explanation")

    if not incidents:
        st.info("No incident is available for copilot explanation.")
        return

    incident_ids = [incident["incident_id"] for incident in incidents]

    with st.container(border=True):
        selected_id = st.selectbox("Incident for copilot", options=incident_ids, key="copilot_incident")
        question = st.text_area(
            "Question",
            value="Why did this incident trigger and what should the technician inspect first?",
            height=95,
        )

        generate = st.button("Generate grounded explanation", type="primary")

    if generate:
        with st.spinner("Calling TwinAgent tools and retrieving engineering context..."):
            copilot = TwinAgentCopilot.from_project_root(PROJECT_ROOT)
            answer = copilot.answer_incident_question(
                incident_id=selected_id,
                question=question,
            )

        st.markdown(
            """
            <div class="section-card">
                <div class="incident-title">Copilot response</div>
                <p class="muted">
                    Generated from incident data, sensor-window evidence, local engineering
                    documents, and deterministic maintenance tools.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_copilot_answer_native(answer)


def render_copilot_answer_native(answer: str) -> None:
    """Render copilot answer using Streamlit-native containers only."""
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

    for index, (title, body_lines) in enumerate(sections, start=1):
        with st.container(border=True):
            st.markdown(f"**{index}. {strip_markdown(title)}**")
            render_copilot_body_lines(body_lines)


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

        # Retrieved source excerpts are plain paragraphs immediately after a source line.
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
