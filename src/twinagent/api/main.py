"""FastAPI backend for TwinAgent AI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from twinagent import PROJECT_NAME, PROJECT_SUBTITLE, __version__
from twinagent.api.dependencies import ApiContext, default_project_root
from twinagent.api.routes_agent import register_agent_routes
from twinagent.api.routes_incidents import register_incident_routes
from twinagent.api.routes_machines import register_machine_routes


OPENAPI_TAGS = [
    {
        "name": "system",
        "description": "Backend health and artifact availability.",
    },
    {
        "name": "machines",
        "description": "Machine-state and sensor-window endpoints backed by SQLite.",
    },
    {
        "name": "incidents",
        "description": "Generated maintenance incidents and suspected-fault details.",
    },
    {
        "name": "agent",
        "description": "Tool-based copilot answers grounded in sensor evidence and retrieved documents.",
    },
]


def create_app(project_root: str | Path | None = None) -> FastAPI:
    """Create and configure the TwinAgent AI FastAPI app."""
    root = Path(project_root) if project_root is not None else default_project_root()
    context = ApiContext(project_root=root)

    app = FastAPI(
        title=PROJECT_NAME,
        description=(
            "Agentic Copilot for Industrial Digital Twins. "
            "This API serves machine state, incidents, sensor windows, and "
            "evidence-grounded copilot explanations for the TwinAgent AI MVP."
        ),
        version=__version__,
        openapi_tags=OPENAPI_TAGS,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "filter": True,
            "docExpansion": "none",
            "syntaxHighlight.theme": "monokai",
        },
    )

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def landing_page() -> str:
        """Return a polished landing page for screenshots and project demos."""
        repository = context.repository()
        database_exists = context.database_path.exists()

        sensor_rows = 0
        incident_count = 0
        latest_health = "N/A"
        latest_risk = "N/A"

        if database_exists:
            sensor_rows = repository.get_sensor_row_count()
            incident_count = repository.get_incident_count()
            try:
                latest = repository.get_latest_machine_state("line1_motor1")
                latest_health = str(latest["health_score"])
                latest_risk = str(latest["risk_level"])
            except ValueError:
                latest_health = "N/A"
                latest_risk = "N/A"

        return _render_landing_page(
            version=__version__,
            sensor_rows=sensor_rows,
            incident_count=incident_count,
            latest_health=latest_health,
            latest_risk=latest_risk,
            database_exists=database_exists,
        )

    @app.get("/health", tags=["system"])
    def health_check() -> dict:
        """Return backend health and artifact availability."""
        repository = context.repository()
        database_exists = context.database_path.exists()

        sensor_rows = 0
        incident_count = 0
        if database_exists:
            sensor_rows = repository.get_sensor_row_count()
            incident_count = repository.get_incident_count()

        return {
            "status": "ok",
            "project": PROJECT_NAME,
            "version": __version__,
            "database_exists": database_exists,
            "sensor_rows": sensor_rows,
            "incident_count": incident_count,
        }

    app.include_router(register_machine_routes(context))
    app.include_router(register_incident_routes(context))
    app.include_router(register_agent_routes(context))

    return app


def _render_landing_page(
    version: str,
    sensor_rows: int,
    incident_count: int,
    latest_health: str,
    latest_risk: str,
    database_exists: bool,
) -> str:
    """Render the premium API landing page."""
    database_status = "Online" if database_exists else "Missing"
    database_class = "good" if database_exists else "warn"

    return f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>TwinAgent AI API</title>
      <style>
        :root {{
          --bg: #07111f;
          --panel: rgba(255, 255, 255, 0.075);
          --panel-2: rgba(255, 255, 255, 0.045);
          --border: rgba(255, 255, 255, 0.14);
          --text: #f8fbff;
          --muted: #a8b6ca;
          --blue: #58a6ff;
          --cyan: #35d0ff;
          --green: #50fa7b;
          --amber: #ffca58;
          --red: #ff6b6b;
        }}

        * {{
          box-sizing: border-box;
        }}

        body {{
          margin: 0;
          min-height: 100vh;
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: var(--text);
          background:
            radial-gradient(circle at 12% 8%, rgba(88, 166, 255, 0.24), transparent 30%),
            radial-gradient(circle at 88% 0%, rgba(53, 208, 255, 0.18), transparent 30%),
            radial-gradient(circle at 55% 92%, rgba(167, 139, 250, 0.15), transparent 34%),
            linear-gradient(135deg, #07111f 0%, #0b1728 45%, #111827 100%);
        }}

        .shell {{
          width: min(1180px, calc(100vw - 40px));
          margin: 0 auto;
          padding: 42px 0 56px;
        }}

        .nav {{
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 34px;
        }}

        .brand {{
          display: flex;
          align-items: center;
          gap: 14px;
        }}

        .logo {{
          width: 46px;
          height: 46px;
          border-radius: 16px;
          display: grid;
          place-items: center;
          background: linear-gradient(135deg, rgba(88, 166, 255, 0.32), rgba(53, 208, 255, 0.18));
          border: 1px solid rgba(88, 166, 255, 0.35);
          box-shadow: 0 14px 40px rgba(88, 166, 255, 0.18);
          font-size: 24px;
        }}

        .brand-title {{
          font-size: 18px;
          font-weight: 900;
          letter-spacing: -0.03em;
        }}

        .brand-sub {{
          color: var(--muted);
          font-size: 13px;
          margin-top: 2px;
        }}

        .badge {{
          padding: 8px 12px;
          border-radius: 999px;
          background: rgba(80, 250, 123, 0.12);
          border: 1px solid rgba(80, 250, 123, 0.25);
          color: #c8ffd7;
          font-weight: 800;
          font-size: 13px;
        }}

        .hero {{
          position: relative;
          overflow: hidden;
          padding: 38px;
          border-radius: 34px;
          background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.58)),
            radial-gradient(circle at 90% 10%, rgba(53, 208, 255, 0.2), transparent 34%);
          border: 1px solid var(--border);
          box-shadow: 0 30px 90px rgba(0, 0, 0, 0.34);
        }}

        .hero::after {{
          content: "";
          position: absolute;
          top: -90px;
          right: -80px;
          width: 260px;
          height: 260px;
          border-radius: 999px;
          background: rgba(88, 166, 255, 0.18);
          filter: blur(50px);
        }}

        .eyebrow {{
          position: relative;
          z-index: 1;
          display: inline-flex;
          padding: 8px 13px;
          border-radius: 999px;
          background: rgba(53, 208, 255, 0.12);
          border: 1px solid rgba(53, 208, 255, 0.28);
          color: #bff2ff;
          font-size: 12px;
          font-weight: 900;
          letter-spacing: 0.11em;
          text-transform: uppercase;
          margin-bottom: 18px;
        }}

        h1 {{
          position: relative;
          z-index: 1;
          margin: 0;
          font-size: clamp(42px, 7vw, 82px);
          line-height: 0.92;
          letter-spacing: -0.065em;
          max-width: 880px;
        }}

        .lead {{
          position: relative;
          z-index: 1;
          margin: 20px 0 0;
          color: var(--muted);
          font-size: 18px;
          line-height: 1.7;
          max-width: 800px;
        }}

        .actions {{
          position: relative;
          z-index: 1;
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          margin-top: 28px;
        }}

        .button {{
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 13px 18px;
          border-radius: 999px;
          text-decoration: none;
          font-weight: 900;
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.18);
          background: linear-gradient(135deg, #2563eb, #06b6d4);
          box-shadow: 0 14px 30px rgba(37, 99, 235, 0.26);
        }}

        .button.secondary {{
          color: #dbeafe;
          background: rgba(255, 255, 255, 0.07);
          box-shadow: none;
        }}

        .grid {{
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
          margin-top: 18px;
        }}

        .card {{
          padding: 20px;
          border-radius: 24px;
          border: 1px solid var(--border);
          background: linear-gradient(180deg, var(--panel), var(--panel-2));
          box-shadow: 0 18px 48px rgba(0, 0, 0, 0.24);
        }}

        .label {{
          color: var(--muted);
          font-size: 12px;
          font-weight: 900;
          letter-spacing: 0.1em;
          text-transform: uppercase;
        }}

        .value {{
          margin-top: 10px;
          font-size: 32px;
          font-weight: 950;
          letter-spacing: -0.055em;
        }}

        .note {{
          margin-top: 8px;
          color: #b8c7dc;
          font-size: 13px;
          line-height: 1.4;
        }}

        .good {{
          color: #b9ffd0;
        }}

        .warn {{
          color: #ffe2a6;
        }}

        .endpoint-grid {{
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 14px;
          margin-top: 16px;
        }}

        .endpoint {{
          padding: 16px;
          border-radius: 20px;
          border: 1px solid rgba(255,255,255,0.11);
          background: rgba(255,255,255,0.052);
        }}

        .method {{
          display: inline-flex;
          padding: 4px 8px;
          border-radius: 8px;
          color: #dbeafe;
          background: rgba(88, 166, 255, 0.18);
          font-size: 12px;
          font-weight: 900;
          margin-bottom: 10px;
        }}

        code {{
          color: #dbeafe;
          font-size: 13px;
          word-break: break-all;
        }}

        h2 {{
          margin: 34px 0 0;
          font-size: 26px;
          letter-spacing: -0.04em;
        }}

        .footer {{
          margin-top: 30px;
          color: var(--muted);
          text-align: center;
          font-size: 13px;
        }}

        @media (max-width: 900px) {{
          .grid, .endpoint-grid {{
            grid-template-columns: 1fr 1fr;
          }}
        }}

        @media (max-width: 640px) {{
          .grid, .endpoint-grid {{
            grid-template-columns: 1fr;
          }}
          .hero {{
            padding: 28px;
          }}
          .nav {{
            align-items: flex-start;
            gap: 18px;
            flex-direction: column;
          }}
        }}
      </style>
    </head>
    <body>
      <main class="shell">
        <nav class="nav">
          <div class="brand">
            <div class="logo">🏭</div>
            <div>
              <div class="brand-title">TwinAgent AI</div>
              <div class="brand-sub">Agentic Copilot for Industrial Digital Twins</div>
            </div>
          </div>
          <div class="badge">v{version} • API online</div>
        </nav>

        <section class="hero">
          <div class="eyebrow">Industrial AI MVP • FastAPI Backend</div>
          <h1>Evidence-grounded maintenance intelligence.</h1>
          <p class="lead">
            Serve machine state, incident windows, SQLite-backed sensor data, and
            deterministic copilot explanations for a simulated conveyor-motor digital twin.
          </p>
          <div class="actions">
            <a class="button" href="/docs">Open Swagger API Docs →</a>
            <a class="button secondary" href="/health">View health JSON</a>
            <a class="button secondary" href="http://127.0.0.1:8501">Open dashboard</a>
          </div>
        </section>

        <section class="grid">
          <div class="card">
            <div class="label">Database</div>
            <div class="value {database_class}">{database_status}</div>
            <div class="note">SQLite artifact availability</div>
          </div>
          <div class="card">
            <div class="label">Sensor rows</div>
            <div class="value">{sensor_rows:,}</div>
            <div class="note">Persisted processed readings</div>
          </div>
          <div class="card">
            <div class="label">Incidents</div>
            <div class="value">{incident_count}</div>
            <div class="note">Generated maintenance events</div>
          </div>
          <div class="card">
            <div class="label">Health / risk</div>
            <div class="value">{latest_health}</div>
            <div class="note">Latest risk level: {latest_risk}</div>
          </div>
        </section>

        <h2>API surface</h2>
        <section class="endpoint-grid">
          <div class="endpoint"><div class="method">GET</div><br><code>/health</code></div>
          <div class="endpoint"><div class="method">GET</div><br><code>/machines/latest</code></div>
          <div class="endpoint"><div class="method">GET</div><br><code>/machines/{{machine_id}}/window</code></div>
          <div class="endpoint"><div class="method">GET</div><br><code>/incidents</code></div>
          <div class="endpoint"><div class="method">GET</div><br><code>/incidents/{{incident_id}}</code></div>
          <div class="endpoint"><div class="method">POST</div><br><code>/agent/incident-question</code></div>
        </section>

        <div class="footer">
          Synthetic-data MVP • Not a certified safety system • Use /docs for interactive API testing
        </div>
      </main>
    </body>
    </html>
    """


app = create_app()
