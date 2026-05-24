"""Hybrid deterministic + AI-backed copilot orchestrator for TwinAgent AI.

The project supports three modes:

- deterministic: free/offline focused answers from trusted local project data.
- ai: use the configured AI provider; if unavailable, fall back cleanly.
- auto: use AI only when TWINAGENT_AI_ENABLED=1 and provider credentials exist.

This version also exposes answer metadata and suggested follow-up questions so
the dashboard can feel more like a real assistant.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import indent
from typing import Any

from twinagent.agent.ai_context import CopilotContextBuilder
from twinagent.agent.ai_provider import LLMResponse, create_llm_provider
from twinagent.agent.copilot_mode import CopilotMode, normalize_copilot_mode
from twinagent.agent.memory import CopilotMemory
from twinagent.agent.prompts import COPILOT_RESPONSE_POLICY
from twinagent.agent.question_intent import (
    CopilotIntent,
    classify_copilot_question,
    suggested_followups_for_intent,
)
from twinagent.agent.tools import TwinAgentTools


SYSTEM_PROMPT = """You are TwinAgent AI, an industrial digital-twin copilot.

Rules:
- Answer only the user's question.
- Use only the provided incident, sensor, document, and memory context.
- Do not invent measurements, machines, incidents, sources, or physical inspection results.
- If the question asks for one fact, answer with one concise fact.
- If the question is messy or misspelled, infer the closest industrial-maintenance intent.
- If the question is unrelated to this machine, incident, sensor data, or maintenance context, say no relevant incident result was found.
- Use "suspected fault" unless there is explicit physical confirmation.
- Mention uncertainty when recommending technician action.
- Do not dump a full report unless the intent is full_report.
"""


@dataclass(frozen=True)
class CopilotAnswer:
    """Structured copilot answer with metadata."""

    answer: str
    incident_id: str
    question: str
    intent: str
    intent_confidence: float
    intent_reason: str
    copilot_mode: str
    provider: str
    model: str
    used_ai: bool
    suggested_followups: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable metadata."""
        return {
            "answer": self.answer,
            "incident_id": self.incident_id,
            "question": self.question,
            "intent": self.intent,
            "intent_confidence": self.intent_confidence,
            "intent_reason": self.intent_reason,
            "copilot_mode": self.copilot_mode,
            "provider": self.provider,
            "model": self.model,
            "used_ai": self.used_ai,
            "suggested_followups": self.suggested_followups,
        }


@dataclass
class TwinAgentCopilot:
    """Tool-using copilot for focused incident Q&A and maintenance guidance."""

    tools: TwinAgentTools
    memory: CopilotMemory | None = None

    @classmethod
    def from_project_root(cls, project_root: str | Path) -> "TwinAgentCopilot":
        """Create a copilot using the default project file layout."""
        root = Path(project_root)
        tools = TwinAgentTools(
            processed_data_path=root / "data" / "processed" / "sensor_data_with_anomalies.csv",
            incidents_path=root / "data" / "incidents" / "incidents.json",
            rag_config_path=root / "configs" / "rag_config.yaml",
            project_root=root,
        )
        memory = CopilotMemory(database_path=root / "data" / "processed" / "copilot_memory.db")
        return cls(tools=tools, memory=memory)

    def answer_incident_question(
        self,
        incident_id: str,
        question: str = "What happened?",
        copilot_mode: str | CopilotMode | None = CopilotMode.AUTO,
    ) -> str:
        """Return only the answer text for backward compatibility."""
        return self.answer_incident_question_with_metadata(
            incident_id=incident_id,
            question=question,
            copilot_mode=copilot_mode,
        ).answer

    def answer_incident_question_with_metadata(
        self,
        incident_id: str,
        question: str = "What happened?",
        copilot_mode: str | CopilotMode | None = CopilotMode.AUTO,
    ) -> CopilotAnswer:
        """Answer an incident question and return answer metadata."""
        incident = self.tools.get_incident(incident_id)
        intent_result = classify_copilot_question(question)
        intent = intent_result.intent
        mode = normalize_copilot_mode(copilot_mode.value if isinstance(copilot_mode, CopilotMode) else copilot_mode)

        deterministic_answer = self._answer_with_rules(
            incident=incident,
            question=question,
            intent=intent,
        )

        response = self._answer_for_mode(
            mode=mode,
            incident=incident,
            question=question,
            intent=intent,
            deterministic_answer=deterministic_answer,
        )

        answer = response.text.strip() if response.text.strip() else deterministic_answer
        followups = suggested_followups_for_intent(intent)

        self._remember(
            question=question,
            answer=answer,
            intent=intent.value,
            provider=response.provider,
            model=response.model,
            incident_id=incident_id,
        )

        return CopilotAnswer(
            answer=answer,
            incident_id=incident_id,
            question=question,
            intent=intent.value,
            intent_confidence=intent_result.confidence,
            intent_reason=intent_result.reason,
            copilot_mode=mode.value,
            provider=response.provider,
            model=response.model,
            used_ai=response.used_ai,
            suggested_followups=followups,
        )

    def _answer_for_mode(
        self,
        mode: CopilotMode,
        incident: dict,
        question: str,
        intent: CopilotIntent,
        deterministic_answer: str,
    ) -> LLMResponse:
        """Generate an answer according to the selected mode."""
        if mode == CopilotMode.DETERMINISTIC:
            return LLMResponse(
                text=deterministic_answer,
                provider="deterministic",
                model="rules",
                used_ai=False,
            )

        provider = create_llm_provider()

        if mode == CopilotMode.AI and not provider.is_available():
            return LLMResponse(
                text=(
                    deterministic_answer
                    + "\n\n_AI mode was selected, but no usable AI provider is available. "
                    "This answer used the local deterministic fallback._"
                ),
                provider="deterministic_ai_unavailable",
                model="rules",
                used_ai=False,
            )

        if mode == CopilotMode.AUTO and not provider.is_available():
            return LLMResponse(
                text=deterministic_answer,
                provider="deterministic",
                model="rules",
                used_ai=False,
            )

        return self._try_ai_answer(
            incident=incident,
            question=question,
            intent=intent,
            deterministic_answer=deterministic_answer,
            provider=provider,
        )

    def _try_ai_answer(
        self,
        incident: dict,
        question: str,
        intent: CopilotIntent,
        deterministic_answer: str,
        provider,
    ) -> LLMResponse:
        """Attempt a real AI answer; fall back cleanly if the provider fails."""
        memory_items = []
        if self.memory is not None:
            memory_items = self.memory.recent_interactions(
                limit=5,
                incident_id=incident.get("incident_id"),
            )

        context_builder = CopilotContextBuilder(tools=self.tools)
        context_package = context_builder.build(
            question=question,
            incident=incident,
            intent=intent,
            memory_items=memory_items,
        )

        user_prompt = (
            "User question:\n"
            f"{question}\n\n"
            "Trusted context package:\n"
            f"{context_package.to_json()}\n\n"
            "Draft deterministic answer, if useful:\n"
            f"{deterministic_answer}\n\n"
            "Write the final answer. Be specific and concise unless full_report is requested."
        )

        try:
            return provider.generate(system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt)
        except Exception:
            return LLMResponse(
                text=deterministic_answer,
                provider="deterministic_after_ai_error",
                model="rules",
                used_ai=False,
            )

    def _remember(
        self,
        question: str,
        answer: str,
        intent: str,
        provider: str,
        model: str,
        incident_id: str | None,
    ) -> None:
        """Persist interaction memory if configured."""
        if self.memory is None:
            return

        self.memory.add_interaction(
            question=question,
            answer=answer,
            intent=intent,
            provider=provider,
            model=model,
            incident_id=incident_id,
        )

    def _answer_with_rules(self, incident: dict, question: str, intent: CopilotIntent) -> str:
        """Return deterministic focused fallback answer."""
        if intent == CopilotIntent.IRRELEVANT:
            return self._answer_irrelevant()

        if intent == CopilotIntent.FULL_REPORT:
            return self._answer_full_report(incident=incident, question=question)

        if intent == CopilotIntent.INCIDENT_TIME:
            return self._answer_incident_time(incident)

        if intent == CopilotIntent.MACHINE_ID:
            return f"The affected machine is `{incident['machine_id']}`."

        if intent == CopilotIntent.MACHINE_FAULT:
            return self._answer_machine_fault(incident, question)

        if intent == CopilotIntent.SEVERITY:
            return (
                f"Incident `{incident['incident_id']}` is classified as "
                f"**{incident['severity']}** severity."
            )

        if intent == CopilotIntent.HEALTH_STATUS:
            return self._answer_health_status(incident)

        if intent == CopilotIntent.ANOMALY_SCORE:
            return (
                f"For incident `{incident['incident_id']}`, the maximum anomaly score was "
                f"**{incident['max_anomaly_score']}** and the mean anomaly score was "
                f"**{incident['mean_anomaly_score']}**."
            )

        if intent == CopilotIntent.SENSOR_EVIDENCE:
            return self._answer_sensor_evidence(incident)

        if intent == CopilotIntent.MAINTENANCE_ACTION:
            return self._answer_maintenance_action(incident, question)

        if intent == CopilotIntent.ENGINEERING_SOURCES:
            return self._answer_engineering_sources(incident, question)

        if intent == CopilotIntent.CURRENT_STATUS:
            return self._answer_current_status()

        return self._answer_incident_summary(incident)

    @staticmethod
    def _answer_irrelevant() -> str:
        """Return a safe no-result response for irrelevant questions."""
        return (
            "No relevant incident result found for that question. "
            "I can answer questions about the current machine state, incident time, suspected fault, "
            "sensor evidence, anomaly score, health score, maintenance actions, or engineering sources."
        )

    @staticmethod
    def _answer_incident_time(incident: dict) -> str:
        """Return only incident timing."""
        duration = incident.get("duration_seconds")
        duration_text = f" Duration: **{duration} seconds**." if duration is not None else ""
        return (
            f"Incident `{incident['incident_id']}` started at `{incident['start_time']}` "
            f"and ended at `{incident['end_time']}`.{duration_text}"
        )

    def _answer_machine_fault(self, incident: dict, question: str) -> str:
        """Return suspected fault and only the strongest reason if asked why."""
        q = question.lower()
        if "why" in q or "cause" in q or "trigger" in q:
            summary = self._window_summary(incident)
            key_sensors = ", ".join(incident.get("contributing_sensors", [])) or "not available"
            return (
                f"The incident was triggered because machine `{incident['machine_id']}` showed a "
                f"high-severity anomaly pattern consistent with suspected **{incident['suspected_fault']}**. "
                f"Main contributing sensors: **{key_sensors}**. Minimum health score in the incident "
                f"window was **{summary['min_health_score']}**, and max anomaly score was "
                f"**{incident['max_anomaly_score']}**."
            )

        return (
            f"The suspected fault for incident `{incident['incident_id']}` is "
            f"**{incident['suspected_fault']}** on machine `{incident['machine_id']}`."
        )

    def _answer_health_status(self, incident: dict) -> str:
        """Return health score for the incident window."""
        summary = self._window_summary(incident)
        return (
            f"During incident `{incident['incident_id']}`, the minimum health score was "
            f"**{summary['min_health_score']}**. The latest health score inside the incident "
            f"window was **{summary['latest_health_score']}**, with risk level "
            f"**{summary['latest_risk_level']}**."
        )

    def _answer_sensor_evidence(self, incident: dict) -> str:
        """Return focused sensor evidence."""
        summary = self._window_summary(incident)
        lines = [f"Key sensor evidence for `{incident['incident_id']}`:"]
        for sensor, sensor_summary in summary["sensor_summary"].items():
            lines.append(
                f"- `{sensor}`: min **{sensor_summary['min']}**, max **{sensor_summary['max']}**, "
                f"start **{sensor_summary['start']}**, end **{sensor_summary['end']}**, "
                f"change **{sensor_summary['change']}**."
            )
        return "\n".join(lines)

    def _answer_maintenance_action(self, incident: dict, question: str) -> str:
        """Return focused maintenance action."""
        checklist = self.tools.generate_maintenance_checklist(
            suspected_fault=str(incident["suspected_fault"]),
            severity=str(incident["severity"]),
        )
        sources = self._retrieve_sources(question, incident, top_k=2)
        actions = "\n".join(f"- {action}" for action in checklist[:4])
        return (
            f"Recommended technician actions for `{incident['incident_id']}`:\n"
            f"{actions}\n\n{self._format_sources_short(sources)}"
        ).strip()

    def _answer_engineering_sources(self, incident: dict, question: str) -> str:
        """Return only retrieved engineering sources."""
        sources = self._retrieve_sources(question, incident, top_k=4)
        if not sources:
            return "No relevant engineering document source was found for this question."

        lines = [f"Relevant engineering sources for `{incident['incident_id']}`:"]
        for source in sources:
            lines.append(f"- `{source.citation}` — {source.title}, {source.heading}")
        return "\n".join(lines)

    def _answer_current_status(self) -> str:
        """Return latest machine status from processed data."""
        dataframe = self.tools.load_processed_data()
        latest = dataframe.sort_values("timestamp").iloc[-1]
        return (
            f"Latest machine status for `{latest['machine_id']}`: state **{latest['machine_state']}**, "
            f"health score **{int(latest['health_score'])}**, risk level **{latest['risk_level']}**, "
            f"maintenance urgency **{latest['maintenance_urgency']}** at "
            f"`{latest['timestamp'].strftime('%Y-%m-%dT%H:%M:%S')}`."
        )

    @staticmethod
    def _answer_incident_summary(incident: dict) -> str:
        """Return a short incident summary."""
        return (
            f"Incident `{incident['incident_id']}` affected machine `{incident['machine_id']}` "
            f"from `{incident['start_time']}` to `{incident['end_time']}`. "
            f"It was classified as **{incident['severity']}** severity with suspected fault "
            f"**{incident['suspected_fault']}**. Max anomaly score: "
            f"**{incident['max_anomaly_score']}**."
        )

    def _answer_full_report(self, incident: dict, question: str) -> str:
        """Return the full report-style answer only when explicitly requested."""
        window_summary = self._window_summary(incident)
        retrieved_sources = self.tools.retrieve_knowledge(
            self._build_retrieval_query(question, incident, window_summary),
            top_k=4,
        )
        checklist = self.tools.generate_maintenance_checklist(
            suspected_fault=str(incident["suspected_fault"]),
            severity=str(incident["severity"]),
        )
        return self._compose_full_answer(
            question=question,
            incident=incident,
            window_summary=window_summary,
            checklist=checklist,
            retrieved_sources=retrieved_sources,
        )

    def _window_summary(self, incident: dict) -> dict:
        """Summarize the incident sensor window."""
        return self.tools.summarize_sensor_window(
            machine_id=str(incident["machine_id"]),
            start_time=str(incident["start_time"]),
            end_time=str(incident["end_time"]),
            contributing_sensors=list(incident.get("contributing_sensors", [])),
        )

    def _retrieve_sources(self, question: str, incident: dict, top_k: int) -> list:
        """Retrieve engineering sources for a focused question."""
        query = (
            f"{question} {incident.get('suspected_fault', '')} "
            f"{' '.join(incident.get('contributing_sensors', []))} "
            "maintenance inspection safety"
        )
        return self.tools.retrieve_knowledge(query, top_k=top_k)

    @staticmethod
    def _format_sources_short(sources: list) -> str:
        """Format short source references."""
        if not sources:
            return "Source: no engineering document matched this specific question."
        lines = ["Supporting sources:"]
        for source in sources:
            lines.append(f"- `{source.citation}`")
        return "\n".join(lines)

    @staticmethod
    def _build_retrieval_query(question: str, incident: dict, window_summary: dict) -> str:
        """Build a retrieval query from the question, fault, and sensor evidence."""
        contributing_sensors = " ".join(incident.get("contributing_sensors", []))
        evidence_terms = " ".join(window_summary.get("sensor_summary", {}).keys())
        return (
            f"{question} {incident.get('suspected_fault', '')} {incident.get('severity', '')} "
            f"{contributing_sensors} {evidence_terms} maintenance inspection safety"
        )

    def _compose_full_answer(
        self,
        question: str,
        incident: dict,
        window_summary: dict,
        checklist: list[str],
        retrieved_sources: list,
    ) -> str:
        """Compose a full grounded incident explanation."""
        lines: list[str] = [
            "# TwinAgent AI Copilot Answer",
            "",
            f"**Question:** {question}",
            "",
            "## 1. Incident summary",
            (
                f"Incident `{incident['incident_id']}` was triggered for "
                f"`{incident['machine_id']}` from `{incident['start_time']}` to "
                f"`{incident['end_time']}`."
            ),
            (
                f"The system classifies this as a **{incident['severity']}** severity incident "
                f"with suspected fault **{incident['suspected_fault']}**."
            ),
            (
                f"The maximum anomaly score was **{incident['max_anomaly_score']}** and the "
                f"mean anomaly score was **{incident['mean_anomaly_score']}**."
            ),
            "",
            "## 2. Sensor evidence",
            (
                f"The queried window contains **{window_summary['rows']}** rows. "
                f"The minimum health score in this window was **{window_summary['min_health_score']}**."
            ),
            "",
        ]

        for sensor, summary in window_summary["sensor_summary"].items():
            lines.append(
                f"- `{sensor}` ranged from **{summary['min']}** to **{summary['max']}** "
                f"(start **{summary['start']}**, end **{summary['end']}**, "
                f"change **{summary['change']}**)."
            )

        if incident.get("evidence"):
            lines.extend(["", "Incident-level evidence from the detector:"])
            for sensor, evidence in incident["evidence"].items():
                lines.append(f"- `{sensor}`: {evidence}")

        lines.extend(["", "## 3. Engineering document guidance"])
        if retrieved_sources:
            for index, source in enumerate(retrieved_sources, start=1):
                excerpt = self._shorten(source.text, max_chars=420)
                lines.append(
                    f"{index}. **{source.title} — {source.heading}** "
                    f"`[{source.citation}]`"
                )
                lines.extend(["", indent(excerpt, prefix="   "), ""])
        else:
            lines.extend(["No relevant knowledge-base source was retrieved.", ""])

        lines.append("## 4. Recommended maintenance actions")
        for action in checklist:
            lines.append(f"- {action}")
        lines.append(f"- Current row-level recommendation: {window_summary['latest_maintenance_recommendation']}")
        lines.extend([
            "",
            "## 5. Uncertainty and limits",
            (
                "- This is a suspected fault based on synthetic sensor evidence and document retrieval, "
                "not physical confirmation."
            ),
            (
                "- A technician inspection is required to confirm real bearing damage, belt misalignment, "
                "cooling failure, or electrical overload."
            ),
            "- The copilot follows this response policy:",
            "",
            indent(COPILOT_RESPONSE_POLICY, prefix="  "),
            "",
        ])
        return "\n".join(lines)

    @staticmethod
    def _shorten(text: str, max_chars: int) -> str:
        """Shorten retrieved text for readable command-line output."""
        normalized = " ".join(text.split())
        if len(normalized) <= max_chars:
            return normalized
        return normalized[: max_chars - 3].rstrip() + "..."
