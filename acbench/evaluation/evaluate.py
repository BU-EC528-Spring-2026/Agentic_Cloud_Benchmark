"""Batch evaluation utilities for the ACBench prototype."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from acbench.agents.profile import apply_agent_profile_to_payload
from acbench.models.runtime import RunConfig
from acbench.orchestrator.runner import ACBenchRunner
from acbench.paths import repo_root, resolve_repo_path


def _resolve_patch_input(
    scenario_path: Path,
    payload: dict[str, Any],
) -> str:
    """Resolve patch input from a prediction entry."""

    scenario = ACBenchRunner().load_scenario(scenario_path)
    if payload.get("use_gold_patch"):
        if not scenario.gold_patch_path:
            raise ValueError(
                f"Scenario {scenario.scenario_id} does not define gold_patch_path."
            )
        return scenario.gold_patch_path
    if payload.get("code_patch_path"):
        return str(payload["code_patch_path"])
    if payload.get("model_patch_path"):
        return str(payload["model_patch_path"])
    if payload.get("model_patch"):
        patch_text = str(payload["model_patch"])
        out_dir = repo_root() / "temp_patches"
        out_dir.mkdir(parents=True, exist_ok=True)
        temp_path = out_dir / f"{scenario.scenario_id}.diff"
        temp_path.write_text(patch_text, encoding="utf-8")
        return str(temp_path)
    return ""


def _build_run_config(
    payload: dict[str, Any],
    *,
    patch_path: str,
) -> RunConfig:
    """Build one RunConfig from one prediction payload."""

    payload = apply_agent_profile_to_payload(payload)
    return RunConfig(
        dry_run=bool(payload.get("dry_run", False)),
        code_patch_path=patch_path,
        aiops_agent_ref=str(payload.get("aiops_agent_ref", "")),
        code_agent_ref=str(payload.get("code_agent_ref", "")),
        agent_config_path=str(payload.get("agent_config_path", payload.get("agent_config", ""))),
        agent_profile_name=str(payload.get("agent_profile_name", "")),
        code_agent_config=dict(payload.get("code_agent_config", {})),
        ops_agent_config=dict(payload.get("ops_agent_config", {})),
        openai_model=str(payload.get("openai_model", "")),
        openai_api_key_env=str(payload.get("openai_api_key_env", "OPENAI_API_KEY")),
        openai_base_url=str(payload.get("openai_base_url", "")),
        anthropic_model=str(payload.get("anthropic_model", "")),
        anthropic_api_key_env=str(
            payload.get("anthropic_api_key_env", "ANTHROPIC_API_KEY")
        ),
        anthropic_base_url=str(
            payload.get("anthropic_base_url", "https://api.anthropic.com")
        ),
        anthropic_version=str(payload.get("anthropic_version", "2023-06-01")),
        max_steps=int(payload.get("max_steps", 10)),
        keep_artifacts=bool(payload.get("keep_artifacts", True)),
    )


def evaluate_predictions(
    manifest_path: str | Path,
    predictions_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    """Evaluate a prediction bundle against a scenario manifest."""

    manifest_file = resolve_repo_path(manifest_path)
    predictions_file = resolve_repo_path(predictions_path)
    output_file = Path(output_path)

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    predictions = json.loads(predictions_file.read_text(encoding="utf-8"))
    prediction_defaults = predictions.get("_defaults", {})
    if prediction_defaults and not isinstance(prediction_defaults, dict):
        raise ValueError("Prediction `_defaults` must be a JSON object when present.")
    runner = ACBenchRunner()

    results: dict[str, Any] = {
        "manifest": str(manifest_file),
        "predictions": str(predictions_file),
        "submitted": 0,
        "success": 0,
        "failure": 0,
        "missing": [],
        "results": {},
        "timing_summary": {},
    }

    for entry in manifest["scenarios"]:
        scenario_path = resolve_repo_path(entry["scenario"])
        scenario = runner.load_scenario(scenario_path)
        pred = predictions.get(scenario.scenario_id)
        if pred is None:
            results["missing"].append(scenario.scenario_id)
            continue
        if not isinstance(pred, dict):
            raise ValueError(
                f"Prediction payload for {scenario.scenario_id} must be a JSON object."
            )

        merged_pred = dict(prediction_defaults)
        merged_pred.update(pred)

        patch_path = _resolve_patch_input(scenario_path, merged_pred)
        run_config = _build_run_config(
            merged_pred,
            patch_path=patch_path,
        )
        run_result = runner.run(
            scenario_path=scenario_path,
            dry_run=run_config.dry_run,
            run_config=run_config,
        )
        code_result = run_result.code_result
        ops_result = run_result.ops_result
        summary = {
            "mode": scenario.mode,
            "status": run_result.status,
            "result_path": run_result.artifacts.result_path,
            "summary_path": run_result.artifacts.summary_path,
            "code_backend": code_result.backend if code_result else "",
            "ops_backend": ops_result.backend if ops_result else "",
            "run_total_seconds": run_result.unified_metrics.get("run_total_seconds", 0.0),
            "build_success": code_result.build_success if code_result else False,
            "test_success": code_result.test_success if code_result else False,
            "detected": ops_result.detected if ops_result else False,
            "localized": ops_result.localized if ops_result else False,
            "repaired": (
                code_result.repaired
                if code_result
                else (ops_result.repaired if ops_result else False)
            ),
            "pass_to_pass_success": code_result.pass_to_pass_success if code_result else [],
            "fail_to_pass_success": code_result.fail_to_pass_success if code_result else [],
            "pass_to_pass_failure": code_result.pass_to_pass_failure if code_result else [],
            "fail_to_pass_failure": code_result.fail_to_pass_failure if code_result else [],
            "code_executor_total_seconds": code_result.metrics.get(
                "executor_total_seconds",
                0.0,
            ) if code_result else 0.0,
            "ops_executor_total_seconds": ops_result.metrics.get(
                "executor_total_seconds",
                0.0,
            ) if ops_result else 0.0,
            "code_agent_answer_count": code_result.metrics.get(
                "agent_answer_count",
                0,
            ) if code_result else 0,
            "ops_agent_answer_count": ops_result.metrics.get(
                "agent_answer_count",
                0,
            ) if ops_result else 0,
            "code_agent_answer_durations_seconds": code_result.metrics.get(
                "agent_answer_durations_seconds",
                [],
            ) if code_result else [],
            "ops_agent_answer_durations_seconds": ops_result.metrics.get(
                "agent_answer_durations_seconds",
                [],
            ) if ops_result else [],
            "code_agent_total_answer_seconds": code_result.metrics.get(
                "agent_total_answer_seconds",
                0.0,
            ) if code_result else 0.0,
            "ops_agent_total_answer_seconds": ops_result.metrics.get(
                "agent_total_answer_seconds",
                0.0,
            ) if ops_result else 0.0,
            "code_agent_average_answer_seconds": code_result.metrics.get(
                "agent_average_answer_seconds",
                0.0,
            ) if code_result else 0.0,
            "ops_agent_average_answer_seconds": ops_result.metrics.get(
                "agent_average_answer_seconds",
                0.0,
            ) if ops_result else 0.0,
        }
        results["results"][scenario.scenario_id] = summary
        results["submitted"] += 1
        if run_result.status == "success":
            results["success"] += 1
        else:
            results["failure"] += 1

    submitted = int(results["submitted"])
    run_total_seconds = sum(
        float(item.get("run_total_seconds", 0.0))
        for item in results["results"].values()
    )
    code_answer_count = sum(
        int(item.get("code_agent_answer_count", 0))
        for item in results["results"].values()
    )
    ops_answer_count = sum(
        int(item.get("ops_agent_answer_count", 0))
        for item in results["results"].values()
    )
    code_total_answer_seconds = sum(
        float(item.get("code_agent_total_answer_seconds", 0.0))
        for item in results["results"].values()
    )
    ops_total_answer_seconds = sum(
        float(item.get("ops_agent_total_answer_seconds", 0.0))
        for item in results["results"].values()
    )
    total_answer_count = code_answer_count + ops_answer_count
    total_answer_seconds = code_total_answer_seconds + ops_total_answer_seconds
    results["timing_summary"] = {
        "scenario_run_total_seconds": round(run_total_seconds, 6),
        "scenario_run_average_seconds": round(
            run_total_seconds / submitted,
            6,
        ) if submitted else 0.0,
        "code_agent_answer_count": code_answer_count,
        "ops_agent_answer_count": ops_answer_count,
        "total_agent_answer_count": total_answer_count,
        "code_agent_total_answer_seconds": round(code_total_answer_seconds, 6),
        "ops_agent_total_answer_seconds": round(ops_total_answer_seconds, 6),
        "total_agent_answer_seconds": round(total_answer_seconds, 6),
        "overall_agent_average_answer_seconds": round(
            total_answer_seconds / total_answer_count,
            6,
        ) if total_answer_count else 0.0,
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results
