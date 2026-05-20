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
Agentic AI copilot prototype for industrial digital-twin workflows, combining synthetic sensor simulation, anomaly detection, RAG-style engineering-document retrieval, dashboarding, evaluation, and evidence-grounded maintenance explanations.
```

---

## Recommended CV entry

```latex
\item{
\textbf{TwinAgent AI: Agentic Copilot for Industrial Digital Twins} \hfill \textit{2026} \\
- Built an agentic AI copilot prototype for industrial digital-twin workflows, combining synthetic conveyor-motor sensor simulation, anomaly detection, predictive-maintenance scoring, RAG-style engineering-document retrieval, and evidence-grounded incident explanations.

- Developed a modular Python pipeline with configurable fault injection, incident generation, health scoring, evaluation metrics, Markdown report export, and an interactive Streamlit dashboard for machine health monitoring and failure analysis.

- Evaluated anomaly detection against known simulated fault labels, reporting precision, recall, F1 score, detection delay, incident overlap, and incident-level diagnosis accuracy while clearly documenting synthetic-data limitations.
}
```

---

## Shorter CV version

```latex
\item{
\textbf{TwinAgent AI: Agentic Copilot for Industrial Digital Twins} \hfill \textit{2026} \\
- Built a modular Python prototype combining synthetic industrial sensor simulation, anomaly detection, health scoring, RAG-style engineering-document retrieval, and evidence-grounded maintenance explanations.

- Developed a Streamlit dashboard, Markdown incident-report export, and evaluation pipeline measuring precision, recall, F1 score, detection delay, incident overlap, and incident-level diagnosis accuracy.
}
```

---

## GitHub tagline

```text
Agentic AI copilot prototype for industrial digital twins, combining synthetic sensor simulation, anomaly detection, engineering-document retrieval, dashboarding, and evidence-grounded incident reports.
```

---

## Interview explanation

### What problem does this solve?

Industrial systems produce sensor data, but detecting an anomaly is not enough. Engineers need to understand what happened, what evidence supports it, which maintenance documents are relevant, and what should be inspected next.

### Why did you use a digital twin?

A synthetic digital twin gives controlled sensor data with known fault labels. That makes it possible to test anomaly detection and evaluate metrics before using real industrial data.

### How does the simulator work?

It generates one-hour conveyor-motor sensor data at 1 Hz. It models normal load variation, sensor noise, temperature, vibration, RPM, current, belt speed, throughput, and injected faults.

### How does anomaly detection work?

The MVP uses interpretable threshold-based scoring. Each sensor contributes a score, and the system combines those scores into an overall anomaly score. Consecutive anomaly rows become incidents.

### How does the copilot work?

The copilot is tool-based. It loads incident data, queries sensor windows, summarizes evidence, retrieves engineering documents, and generates a grounded response with recommended actions and uncertainty statements.

### How do you reduce hallucinations?

The copilot does not answer from memory alone. It separates sensor evidence from document guidance and includes citations to retrieved knowledge-base sections.

### What are the limitations?

The data is synthetic, and the health score is a proxy. The system is not a certified safety system and does not claim real-world predictive-maintenance accuracy.

### How would you improve it with real data?

I would calibrate thresholds using historical maintenance data, validate sensor ranges, compare multiple anomaly detectors, integrate a real time-series database, and connect real machine logs or MQTT streams.

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
```

Avoid:

```text
production-ready
certified
real factory deployment
guaranteed fault diagnosis
real-world predictive-maintenance accuracy
```
