# Copilot Modes

TwinAgent AI supports three copilot modes.

---

## 1. Deterministic mode

```text
deterministic
```

This mode is free and offline. It answers from local project data only:

- incidents JSON
- processed sensor CSV
- SQLite outputs
- engineering-document retriever
- deterministic maintenance rules

Use this for:

- GitHub demos
- interviews
- offline use
- environments without API billing
- reliable factual answers

---

## 2. AI mode

```text
ai
```

This mode tries to call the configured AI provider.

To enable OpenAI API usage:

```cmd
set TWINAGENT_AI_ENABLED=1
set OPENAI_API_KEY=your_key_here
set TWINAGENT_LLM_MODEL=gpt-4o-mini
```

If the provider is unavailable, the system falls back to deterministic answers.

---

## 3. Auto mode

```text
auto
```

This is the default. It uses AI only when the API provider is configured and available. Otherwise, it uses deterministic mode.

---

## Dashboard usage

In the copilot tab, choose:

```text
Deterministic (free/local)
AI-assisted (OpenAI API)
Auto
```

---

## API usage

POST body:

```json
{
  "incident_id": "INC-0001",
  "question": "when did the incident happen?",
  "copilot_mode": "deterministic"
}
```

Allowed values:

```text
deterministic
ai
auto
```

---

## Recommendation

For portfolio demonstration, use deterministic mode by default because it works everywhere.

For a stronger real-AI demo, use AI mode only after configuring OpenAI API billing and quota.
