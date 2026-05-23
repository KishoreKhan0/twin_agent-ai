# AI Copilot Upgrade

TwinAgent AI now supports a hybrid copilot:

1. **Deterministic fallback mode** — works without API keys.
2. **Real AI mode** — uses an OpenAI-compatible provider when enabled.

The AI mode does not blindly send the full incident report. It first classifies the question, builds a minimal trusted context package, and then asks the model to answer only the user's question.

---

## Enable AI mode

Install dependencies:

```cmd
pip install -r requirements.txt
```

Set environment variables in Windows CMD:

```cmd
set TWINAGENT_AI_ENABLED=1
set OPENAI_API_KEY=your_key_here
set TWINAGENT_LLM_MODEL=gpt-4o-mini
```

Then run:

```cmd
python scripts\bootstrap_demo_data.py
python scripts\launch_dashboard.py
```

---

## Behavior

Short factual questions should stay short:

```text
incident time?
```

Expected answer:

```text
Incident INC-0001 started at ... and ended at ...
```

A full report is returned only when requested:

```text
give me the full report
```

Irrelevant questions return a no-result response.

---

## Why this architecture

The model is not allowed to invent machine data. It receives only trusted context from:

- incident JSON
- processed sensor CSV
- SQLite-backed latest state
- local engineering-document retrieval
- recent copilot memory

The deterministic fallback remains available for offline demos and testing.
