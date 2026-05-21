# CV Notes

This document captures how to honestly present TwinAgent AI on a CV, GitHub, and in interviews.

---

## Project title

```text
TwinAgent AI: Agentic Copilot for Industrial Digital Twins
```

---

## One-line CV pitch

```text
End-to-end agentic AI copilot prototype for industrial digital-twin workflows, combining synthetic sensor simulation, anomaly detection, maintenance scoring, RAG-style engineering-document retrieval, API/dashboard serving, Dockerized deployment, and evidence-grounded incident explanations.
```

---

## Recommended CV entry

```latex
\item{
\textbf{TwinAgent AI: Agentic Copilot for Industrial Digital Twins} \hfill \textit{2026} \\
- Built an end-to-end agentic AI copilot prototype for industrial digital-twin workflows, combining synthetic conveyor-motor sensor simulation, anomaly detection, predictive-maintenance scoring, RAG-style engineering-document retrieval, and evidence-grounded incident explanations.

- Developed a modular Python system with SQLite persistence, MQTT-style sensor streaming, FastAPI backend, Streamlit dashboard, Docker Compose demo, Markdown incident-report export, and automated evaluation against known simulated fault labels.

- Evaluated anomaly detection using precision, recall, F1 score, detection delay, incident overlap, and incident-level diagnosis accuracy while clearly documenting synthetic-data limitations.
}
```

---

## Shorter CV version

```latex
\item{
\textbf{TwinAgent AI: Agentic Copilot for Industrial Digital Twins} \hfill \textit{2026} \\
- Built a modular Python prototype combining synthetic industrial sensor simulation, anomaly detection, health scoring, RAG-style engineering-document retrieval, and evidence-grounded maintenance explanations.

- Developed SQLite persistence, MQTT-style replay, FastAPI endpoints, Streamlit dashboard, Docker Compose demo, Markdown incident reports, and evaluation metrics over known simulated fault labels.
}
```

---

## GitHub tagline

```text
Agentic AI copilot prototype for industrial digital twins, combining synthetic sensor simulation, anomaly detection, engineering-document retrieval, FastAPI, Streamlit, SQLite, MQTT-style replay, Docker, and evidence-grounded incident reports.
```

---

## Interview explanation

### What problem does this solve?

Industrial anomaly alerts are not enough by themselves. Engineers need evidence, context, documentation, and recommended next actions. TwinAgent AI demonstrates how sensor analytics and agentic AI tools can support that workflow.

### Why did you use a digital twin?

A synthetic digital twin gives controlled sensor data with known fault labels, allowing me to evaluate anomaly detection and incident diagnosis before using real industrial data.

### How does the simulator work?

It generates one-hour conveyor-motor sensor data at 1 Hz. It models load variation, temperature, vibration, RPM, current, belt speed, throughput, ambient temperature, and injected faults.

### How does anomaly detection work?

The MVP uses interpretable threshold-based scoring. Each sensor contributes a score, and consecutive anomaly rows are grouped into incidents.

### How does the copilot work?

The copilot is tool-based. It loads incidents, queries sensor windows, summarizes evidence, retrieves engineering documents, and generates a grounded response with maintenance actions and uncertainty statements.

### Why deterministic before LLM?

The deterministic tool layer makes the system testable, reproducible, and safe from hallucinating unsupported evidence. An LLM can later be added on top of the same tools.

### How is it served?

The project includes both a Streamlit dashboard and a FastAPI backend. Docker Compose can run both services.

### What are the limitations?

The data is synthetic, the health score is a proxy, and the project is not a certified safety or production predictive-maintenance system.

---

## Good wording

Use:

```text
prototype
synthetic digital twin
simulated sensor stream
evidence-grounded explanation
RAG-style retrieval
predictive-maintenance scoring proxy
incident-level diagnosis
Dockerized local demo
```

Avoid:

```text
production-ready
certified
real factory deployment
guaranteed fault diagnosis
real-world predictive-maintenance accuracy
```
