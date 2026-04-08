"""Execution adapters for the internal standalone ACBench ops runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from acbench.agents.loader import load_object
from acbench.executors.backends.ops.runtime import (
    NativeOpsProblem,
    OpsRunOutcome,
    OpsRunRequest,
)


class OpsRuntimeEngine(Protocol):
    """Protocol for pluggable ACBench ops runtime engines."""

    def run(self, request: OpsRunRequest) -> OpsRunOutcome:
        """Execute one ops-task request and return a normalized outcome."""


@dataclass(slots=True)
class StandaloneLocalOpsEngine:
    """ACBench-owned synthetic ops engine for local development and demos."""

    def run(self, request: OpsRunRequest) -> OpsRunOutcome:
        """Produce a deterministic synthetic ops outcome."""

        problem = request.problem
        metrics = {
            "TTD": 1.0 if problem.require_detection else 0.0,
            "TTL": 2.0 if problem.require_localization else 0.0,
            "TTM": 3.0 if problem.require_repair else 0.0,
            "synthetic": True,
        }
        return OpsRunOutcome(
            detected=problem.require_detection,
            localized=problem.require_localization,
            repaired=problem.require_repair,
            success=True,
            metrics=metrics,
            details={
                "mode": "synthetic-local-ops",
                "problem_id": problem.problem_id,
                "max_steps": request.max_steps,
                "agent_ref": request.agent_ref,
            },
        )


@dataclass(slots=True)
class AgentDrivenOpsEngine:
    """Run one ops task through a configured agent and score it with a rubric."""

    def run(self, request: OpsRunRequest) -> OpsRunOutcome:
        agent_cls = load_object(request.agent_ref)
        agent = agent_cls()
        if hasattr(agent, "configure"):
            agent.configure(
                run_config=request,
                model=request.openai_model,
                api_key_env=request.openai_api_key_env,
                base_url=request.openai_base_url,
                anthropic_model=request.anthropic_model,
                anthropic_api_key_env=request.anthropic_api_key_env,
                anthropic_base_url=request.anthropic_base_url,
                anthropic_version=request.anthropic_version,
            )
        if not hasattr(agent, "analyze"):
            raise ValueError(
                f"Configured ops agent `{request.agent_ref}` does not expose `analyze`."
            )

        artifacts = agent.analyze(
            request.problem,
            output_dir=request.output_dir,
        )
        assessment = dict(artifacts.get("assessment", {}))
        detection_match = _rubric_match(
            assessment,
            request.problem.detection_keywords,
            sections=("summary", "root_cause", "evidence"),
        )
        localization_match = _rubric_match(
            assessment,
            request.problem.localization_keywords,
            sections=("root_cause", "summary", "evidence"),
        )
        repair_match = _rubric_match(
            assessment,
            request.problem.repair_keywords,
            sections=("remediation", "root_cause", "summary", "evidence"),
        )

        detected = (
            assessment.get("detected", False) and detection_match
            if request.problem.require_detection
            else True
        )
        localized = (
            assessment.get("localized", False) and localization_match
            if request.problem.require_localization
            else True
        )
        repaired = (
            assessment.get("repaired", False) and repair_match
            if request.problem.require_repair
            else True
        )

        return OpsRunOutcome(
            detected=detected,
            localized=localized,
            repaired=repaired,
            success=all(
                [
                    detected if request.problem.require_detection else True,
                    localized if request.problem.require_localization else True,
                    repaired if request.problem.require_repair else True,
                ]
            ),
            metrics={
                "TTD": 1.0 if detected else 0.0,
                "TTL": 2.0 if localized else 0.0,
                "TTM": 3.0 if repaired else 0.0,
                "synthetic": False,
                "agent_ref": request.agent_ref,
                "rubric_detection_match": detection_match,
                "rubric_localization_match": localization_match,
                "rubric_repair_match": repair_match,
                "agent_answer_count": int(artifacts.get("telemetry", {}).get("answer_count", 0)),
                "agent_answer_durations_seconds": list(
                    artifacts.get("telemetry", {}).get("answer_durations_seconds", [])
                ),
                "agent_total_answer_seconds": float(
                    artifacts.get("telemetry", {}).get("total_answer_seconds", 0.0)
                ),
                "agent_average_answer_seconds": float(
                    artifacts.get("telemetry", {}).get("average_answer_seconds", 0.0)
                ),
                "agent_wall_time_seconds": float(
                    artifacts.get("telemetry", {}).get("wall_time_seconds", 0.0)
                ),
            },
            logs={
                "prompt_path": str(artifacts.get("prompt_path", "")),
                "response_path": str(artifacts.get("response_path", "")),
                "assessment_path": str(artifacts.get("assessment_path", "")),
                "agent_telemetry_path": str(artifacts.get("telemetry_path", "")),
            },
            details={
                "mode": "agent-driven-ops",
                "problem_id": request.problem.problem_id,
                "max_steps": request.max_steps,
                "agent_ref": request.agent_ref,
                "assessment": assessment,
                "agent_telemetry": artifacts.get("telemetry", {}),
                "matched_detection_keywords": _matched_keywords(
                    assessment,
                    request.problem.detection_keywords,
                    sections=("summary", "root_cause", "evidence"),
                ),
                "matched_localization_keywords": _matched_keywords(
                    assessment,
                    request.problem.localization_keywords,
                    sections=("root_cause", "summary", "evidence"),
                ),
                "matched_repair_keywords": _matched_keywords(
                    assessment,
                    request.problem.repair_keywords,
                    sections=("remediation", "root_cause", "summary", "evidence"),
                ),
            },
        )


def build_default_engine() -> OpsRuntimeEngine:
    """Build the default standalone ops runtime engine."""

    return StandaloneLocalOpsEngine()


def build_engine_for_problem(problem: NativeOpsProblem) -> OpsRuntimeEngine:
    """Build the most appropriate current engine for one ops problem."""

    return build_default_engine()


def build_engine_for_request(request: OpsRunRequest) -> OpsRuntimeEngine:
    """Select the best engine for one normalized ops request."""

    if request.agent_ref:
        return AgentDrivenOpsEngine()
    return build_engine_for_problem(request.problem)


def _joined_sections(assessment: dict[str, object], sections: tuple[str, ...]) -> str:
    parts: list[str] = []
    for section in sections:
        value = assessment.get(section, "")
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
        else:
            parts.append(str(value))
    return " ".join(parts).lower()


def _matched_keywords(
    assessment: dict[str, object],
    keywords: list[str],
    *,
    sections: tuple[str, ...],
) -> list[str]:
    if not keywords:
        return []
    haystack = _joined_sections(assessment, sections)
    return [keyword for keyword in keywords if keyword.lower() in haystack]


def _rubric_match(
    assessment: dict[str, object],
    keywords: list[str],
    *,
    sections: tuple[str, ...],
) -> bool:
    if not keywords:
        return True
    return bool(_matched_keywords(assessment, keywords, sections=sections))
