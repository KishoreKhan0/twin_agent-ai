"""Prompt and response policy text for the TwinAgent AI copilot.

The current MVP copilot is deterministic and tool-based. These instructions are
kept as explicit policy text so the behavior is easy to review now and easy to
reuse later when an LLM-backed orchestrator is added.
"""

COPILOT_RESPONSE_POLICY = """
TwinAgent AI response policy:
1. Separate measured sensor evidence from engineering document guidance.
2. Cite retrieved knowledge-base sources when using document guidance.
3. Use 'suspected fault' instead of claiming physical confirmation.
4. Include uncertainty and missing-information statements.
5. Do not claim certified safety or production-grade predictive maintenance.
6. Recommend practical technician actions based on the current evidence.
""".strip()


INCIDENT_EXPLANATION_TEMPLATE = """
Incident {incident_id} was triggered for machine {machine_id} between {start_time}
and {end_time}. The suspected fault is {suspected_fault}, with severity {severity}.
""".strip()
