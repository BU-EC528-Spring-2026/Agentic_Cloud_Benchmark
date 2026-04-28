"""Scenario scoring helpers for richer evaluation output."""

from __future__ import annotations

from typing import Any

from acbench.models.result import BenchmarkResult, ExecutorResult
from acbench.models.scenario import ScenarioSpec


CODE_COMPONENT_WEIGHTS = {
    "build": 0.15,
    "test": 0.15,
    "fail_to_pass": 0.45,
    "pass_to_pass": 0.25,
}

OPS_COMPONENT_WEIGHTS = {
    "detection": 0.30,
    "localization": 0.30,
    "remediation": 0.40,
}

COMBINED_STAGE_WEIGHTS = {
    "ops": 0.50,
    "code": 0.50,
}


def build_scorecard(
    scenario: ScenarioSpec,
    result: BenchmarkResult,
) -> dict[str, Any]:
    """Build a stable scorecard for one scenario result."""

    breakdown: dict[str, Any] = {}
    failure_reasons: list[str] = []
    stage_scores: dict[str, float] = {}

    if result.ops_result is not None:
        ops_score, ops_breakdown, ops_failures = _score_ops(
            scenario,
            result.ops_result,
        )
        stage_scores["ops"] = ops_score
        breakdown["ops"] = ops_breakdown
        failure_reasons.extend(f"ops:{reason}" for reason in ops_failures)

    if result.code_result is not None:
        code_score, code_breakdown, code_failures = _score_code(
            scenario,
            result.code_result,
        )
        stage_scores["code"] = code_score
        breakdown["code"] = code_breakdown
        failure_reasons.extend(f"code:{reason}" for reason in code_failures)

    final_score, overall_breakdown = _score_overall(stage_scores)
    breakdown["overall"] = overall_breakdown

    return {
        "final_score": _round(final_score),
        "ops_score": _round(stage_scores.get("ops", 0.0)),
        "code_score": _round(stage_scores.get("code", 0.0)),
        "score_breakdown": breakdown,
        "failure_reasons": _dedupe_keep_order(failure_reasons),
    }


def _score_code(
    scenario: ScenarioSpec,
    result: ExecutorResult,
) -> tuple[float, dict[str, Any], list[str]]:
    weights: dict[str, float] = {}
    components: dict[str, float] = {}
    counts: dict[str, int] = {}
    failures: list[str] = []

    expected_fail_to_pass = len(scenario.evaluation.fail_to_pass)
    expected_pass_to_pass = len(scenario.evaluation.pass_to_pass)

    if scenario.success_criteria.require_build_success or scenario.build.rebuild_cmds:
        weights["build"] = CODE_COMPONENT_WEIGHTS["build"]
        components["build"] = 1.0 if result.build_success else 0.0
        if not result.build_success:
            failures.append("build_failed")

    if scenario.success_criteria.require_test_success or scenario.build.test_cmds:
        weights["test"] = CODE_COMPONENT_WEIGHTS["test"]
        components["test"] = 1.0 if result.test_success else 0.0
        if not result.test_success:
            failures.append("tests_failed")

    if expected_fail_to_pass:
        weights["fail_to_pass"] = CODE_COMPONENT_WEIGHTS["fail_to_pass"]
        components["fail_to_pass"] = _ratio(
            len(result.fail_to_pass_success),
            expected_fail_to_pass,
        )
        counts["fail_to_pass_expected"] = expected_fail_to_pass
        counts["fail_to_pass_success"] = len(result.fail_to_pass_success)
        counts["fail_to_pass_failure"] = len(result.fail_to_pass_failure)
        if result.fail_to_pass_failure:
            failures.append("fail_to_pass_incomplete")

    if expected_pass_to_pass:
        weights["pass_to_pass"] = CODE_COMPONENT_WEIGHTS["pass_to_pass"]
        components["pass_to_pass"] = _ratio(
            len(result.pass_to_pass_success),
            expected_pass_to_pass,
        )
        counts["pass_to_pass_expected"] = expected_pass_to_pass
        counts["pass_to_pass_success"] = len(result.pass_to_pass_success)
        counts["pass_to_pass_failure"] = len(result.pass_to_pass_failure)
        if result.pass_to_pass_failure:
            failures.append("pass_to_pass_regression")

    if result.details.get("apply_success") is False:
        failures.append("patch_apply_failed")

    final_score, normalized_weights = _weighted_score(components, weights)
    return (
        final_score,
        {
            "stage_score": _round(final_score),
            "components": {key: _round(value) for key, value in components.items()},
            "weights": {key: _round(value) for key, value in normalized_weights.items()},
            "counts": counts,
            "success": result.success,
        },
        failures,
    )


def _score_ops(
    scenario: ScenarioSpec,
    result: ExecutorResult,
) -> tuple[float, dict[str, Any], list[str]]:
    weights: dict[str, float] = {}
    components: dict[str, float] = {}
    keyword_match_ratios: dict[str, float] = {}
    failures: list[str] = []

    assessment = result.details.get("assessment", {})
    if not isinstance(assessment, dict):
        assessment = {}

    if scenario.success_criteria.require_detection:
        weights["detection"] = OPS_COMPONENT_WEIGHTS["detection"]
        components["detection"] = _ops_component_score(
            raw_flag=bool(assessment.get("detected", result.detected)),
            matched_keywords=result.details.get("matched_detection_keywords", []),
            expected_keywords=scenario.ops_fault.detection_keywords if scenario.ops_fault else [],
            fallback_flag=result.detected,
        )
        keyword_match_ratios["detection"] = _keyword_ratio(
            result.details.get("matched_detection_keywords", []),
            scenario.ops_fault.detection_keywords if scenario.ops_fault else [],
            result.detected,
        )
        if not result.detected:
            failures.append("detection_incomplete")

    if scenario.success_criteria.require_localization:
        weights["localization"] = OPS_COMPONENT_WEIGHTS["localization"]
        components["localization"] = _ops_component_score(
            raw_flag=bool(assessment.get("localized", result.localized)),
            matched_keywords=result.details.get("matched_localization_keywords", []),
            expected_keywords=scenario.ops_fault.localization_keywords if scenario.ops_fault else [],
            fallback_flag=result.localized,
        )
        keyword_match_ratios["localization"] = _keyword_ratio(
            result.details.get("matched_localization_keywords", []),
            scenario.ops_fault.localization_keywords if scenario.ops_fault else [],
            result.localized,
        )
        if not result.localized:
            failures.append("localization_incomplete")

    if scenario.success_criteria.require_repair:
        weights["remediation"] = OPS_COMPONENT_WEIGHTS["remediation"]
        components["remediation"] = _ops_component_score(
            raw_flag=bool(assessment.get("repaired", result.repaired)),
            matched_keywords=result.details.get("matched_repair_keywords", []),
            expected_keywords=scenario.ops_fault.repair_keywords if scenario.ops_fault else [],
            fallback_flag=result.repaired,
        )
        keyword_match_ratios["remediation"] = _keyword_ratio(
            result.details.get("matched_repair_keywords", []),
            scenario.ops_fault.repair_keywords if scenario.ops_fault else [],
            result.repaired,
        )
        if not result.repaired:
            failures.append("remediation_incomplete")

    final_score, normalized_weights = _weighted_score(components, weights)
    return (
        final_score,
        {
            "stage_score": _round(final_score),
            "components": {key: _round(value) for key, value in components.items()},
            "weights": {key: _round(value) for key, value in normalized_weights.items()},
            "keyword_match_ratios": {
                key: _round(value) for key, value in keyword_match_ratios.items()
            },
            "success": result.success,
        },
        failures,
    )


def _score_overall(stage_scores: dict[str, float]) -> tuple[float, dict[str, Any]]:
    if not stage_scores:
        return 0.0, {
            "stage_score": 0.0,
            "components": {},
            "weights": {},
        }
    if len(stage_scores) == 1:
        stage_name, stage_score = next(iter(stage_scores.items()))
        return stage_score, {
            "stage_score": _round(stage_score),
            "components": {stage_name: _round(stage_score)},
            "weights": {stage_name: 1.0},
        }

    weights = {
        stage_name: COMBINED_STAGE_WEIGHTS.get(stage_name, 0.0)
        for stage_name in stage_scores
    }
    final_score, normalized_weights = _weighted_score(stage_scores, weights)
    return final_score, {
        "stage_score": _round(final_score),
        "components": {key: _round(value) for key, value in stage_scores.items()},
        "weights": {key: _round(value) for key, value in normalized_weights.items()},
    }


def _ops_component_score(
    *,
    raw_flag: bool,
    matched_keywords: object,
    expected_keywords: list[str],
    fallback_flag: bool,
) -> float:
    keyword_score = _keyword_ratio(
        matched_keywords,
        expected_keywords,
        fallback_flag,
    )
    bool_score = 1.0 if raw_flag else 0.0
    return (0.5 * bool_score) + (0.5 * keyword_score)


def _keyword_ratio(
    matched_keywords: object,
    expected_keywords: list[str],
    fallback_flag: bool,
) -> float:
    if expected_keywords:
        if isinstance(matched_keywords, list):
            return min(len(matched_keywords), len(expected_keywords)) / len(expected_keywords)
        return 0.0
    return 1.0 if fallback_flag else 0.0


def _weighted_score(
    components: dict[str, float],
    weights: dict[str, float],
) -> tuple[float, dict[str, float]]:
    if not components or not weights:
        return 0.0, {}
    total_weight = sum(weight for key, weight in weights.items() if key in components)
    if total_weight <= 0:
        return 0.0, {}
    normalized_weights = {
        key: weight / total_weight
        for key, weight in weights.items()
        if key in components
    }
    final_score = sum(components[key] * normalized_weights[key] for key in normalized_weights)
    return final_score, normalized_weights


def _ratio(success_count: int, expected_count: int) -> float:
    if expected_count <= 0:
        return 1.0
    return min(success_count, expected_count) / expected_count


def _round(value: float) -> float:
    return round(float(value), 6)


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
