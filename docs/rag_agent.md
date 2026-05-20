# RAG and Agentic Copilot

TwinAgent AI includes a local retrieval layer and a deterministic tool-based copilot.

---

## Knowledge base

The MVP uses synthetic but realistic Markdown engineering documents:

```text
knowledge_base/motor_manual.md
knowledge_base/conveyor_maintenance_guide.md
knowledge_base/fault_code_reference.md
knowledge_base/safety_checklist.md
knowledge_base/bearing_failure_notes.md
knowledge_base/sensor_specs.md
knowledge_base/maintenance_log_q1.md
```

These documents contain:

- normal operating limits
- high-temperature guidance
- high-vibration guidance
- bearing inspection procedure
- belt misalignment procedure
- safety checklist
- fault code descriptions
- maintenance history notes

---

## Retrieval approach

The MVP uses a local TF-IDF-style retriever.

Pipeline:

```text
Markdown documents
        ↓
document loader
        ↓
chunker
        ↓
local vector representation
        ↓
top-k retrieval
        ↓
citation-friendly chunks
```

The retriever returns:

```text
source file
chunk ID
title
heading
score
text
citation string
```

Example citation format:

```text
conveyor_maintenance_guide.md::Bearing Inspection Procedure
```

---

## Why not external embeddings yet?

The MVP avoids external embedding downloads because:

- the project must run easily on Windows
- no API keys should be required for the core demo
- deterministic behavior is easier to test
- the retrieval API can later be upgraded to ChromaDB or FAISS

---

## Agent tools

The copilot uses tools instead of answering from a prompt alone.

Available tools include:

```text
load_processed_data
load_incidents
list_recent_incidents
get_incident
query_sensor_window
summarize_sensor_window
retrieve_knowledge
generate_maintenance_checklist
```

---

## Copilot behavior

For an incident question, the copilot:

1. loads the incident
2. queries the sensor window
3. summarizes contributing sensors
4. retrieves relevant engineering documents
5. creates a maintenance checklist
6. generates a grounded answer

The answer includes:

- incident summary
- sensor evidence
- engineering document guidance
- recommended actions
- uncertainty and limits

---

## Example question

```text
Why did this incident trigger and what should the technician inspect first?
```

---

## Hallucination control

The copilot follows these rules:

```text
1. Separate measured sensor evidence from engineering document guidance.
2. Cite retrieved knowledge-base sources when using document guidance.
3. Use suspected fault instead of claiming physical confirmation.
4. Include uncertainty and missing-information statements.
5. Do not claim certified safety or production-grade predictive maintenance.
6. Recommend practical technician actions based on current evidence.
```

---

## Current limitation

The MVP copilot is deterministic and template-based. This is intentional. A later LLM-backed version can call the same tools and use the same response policy.
