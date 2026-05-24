# Natural Copilot Questions

TwinAgent AI supports structured and messy natural questions in deterministic mode and AI-assisted mode.

---

## Examples

```text
issue when?
```

Returns the incident time window.

```text
wat happend bro
```

Returns a concise incident summary.

```text
what wrong with motor
```

Returns the suspected machine fault.

```text
is it bad?
```

Returns the incident severity.

```text
what should i do now?
```

Returns technician inspection actions.

---

## Metadata

The copilot now produces answer metadata:

- detected intent
- confidence
- reason
- selected copilot mode
- provider
- model
- suggested follow-up questions

The dashboard uses this metadata to show suggested next questions and recent answer history.

---

## Why this matters

A useful industrial copilot should not require perfect prompt wording. It should understand operational shorthand and still answer from trusted data.
