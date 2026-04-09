"""OpenAI-backed code agent integrations for ACBench."""

from __future__ import annotations

import os
import json
from pathlib import Path
import re
from time import perf_counter
from typing import Any

from openai import OpenAI

from acbench.agents.telemetry import summarize_call_records, timed_call
from acbench.models.runtime import RunConfig
from acbench.models.scenario import ScenarioSpec
from acbench.paths import resolve_repo_path


class OpenAICodePatchAgent:
    """Generate a unified diff patch for standalone repository-backed code tasks."""

    def generate_patch(
        self,
        scenario: ScenarioSpec,
        run_config: RunConfig,
        *,
        output_dir: Path,
    ) -> dict[str, str]:
        section = dict(run_config.code_agent_config or {})
        model = str(section.get("model", run_config.openai_model)).strip()
        api_key_env = str(
            section.get(
                "api_key_env",
                run_config.openai_api_key_env or "OPENAI_API_KEY",
            )
        ).strip()
        base_url = str(section.get("base_url", run_config.openai_base_url or "")).strip()

        api_key = os.environ.get(api_key_env or "OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError(
                f"Environment variable `{api_key_env}` is not set."
            )
        if not model:
            raise ValueError("RunConfig.openai_model is required for OpenAICodePatchAgent.")

        prompt = self._build_prompt(scenario)
        client = OpenAI(
            api_key=api_key,
            base_url=base_url or None,
        )
        started = perf_counter()
        call_records: list[dict[str, Any]] = []
        response, call_record = timed_call(
            "initial_answer",
            client.responses.create,
            model=model,
            input=prompt,
        )
        call_records.append(call_record)
        raw_text = getattr(response, "output_text", "") or ""
        prompt_path = output_dir / "openai_prompt.txt"
        response_path = output_dir / "openai_response.txt"
        telemetry_path = output_dir / "openai_code_telemetry.json"
        prompt_path.write_text(prompt, encoding="utf-8")
        response_path.write_text(raw_text, encoding="utf-8")
        patch_text = self._extract_patch(raw_text)
        patch_text = self._normalize_unified_diff(patch_text)
        validation_error = self._validate_unified_diff(patch_text)
        for _ in range(3):
            if not validation_error:
                break
            repair_prompt = self._build_patch_repair_prompt(
                original_prompt=prompt,
                invalid_patch=patch_text,
                validation_error=validation_error,
            )
            repair_response, call_record = timed_call(
                f"repair_answer_{len(call_records)}",
                client.responses.create,
                model=model,
                input=repair_prompt,
            )
            call_records.append(call_record)
            repair_text = getattr(repair_response, "output_text", "") or ""
            raw_text = f"{raw_text}\n\n--- PATCH REPAIR ---\n{repair_text}"
            response_path.write_text(raw_text, encoding="utf-8")
            patch_text = self._extract_patch(repair_text)
            patch_text = self._normalize_unified_diff(patch_text)
            validation_error = self._validate_unified_diff(patch_text)
        telemetry = summarize_call_records(
            call_records,
            wall_time_seconds=perf_counter() - started,
        )
        telemetry_path.write_text(json.dumps(telemetry, indent=2), encoding="utf-8")
        if validation_error:
            raise ValueError(f"Model returned an invalid unified diff after retries: {validation_error}")

        patch_path = output_dir / "openai_generated_patch.diff"
        patch_path.write_text(patch_text, encoding="utf-8")
        return {
            "patch_text": patch_text,
            "prompt_path": str(prompt_path),
            "response_path": str(response_path),
            "generated_patch_path": str(patch_path),
            "telemetry": telemetry,
            "telemetry_path": str(telemetry_path),
        }

    def _build_prompt(self, scenario: ScenarioSpec) -> str:
        repository_path = scenario.service.repository_path or ""
        if repository_path:
            repo_root = resolve_repo_path(repository_path)
            return self._build_repository_prompt(scenario, repo_root)
        raise ValueError("OpenAICodePatchAgent requires service.repository_path.")

    def _build_repository_prompt(self, scenario: ScenarioSpec, repo_root: Path) -> str:
        target_files = list(scenario.code_fault.target_files if scenario.code_fault else [])
        if not target_files:
            target_files = self._discover_default_targets(repo_root)

        sections = [
            "You are fixing a repository-backed benchmark task.",
            "Return only a valid unified diff patch.",
            f"Scenario ID: {scenario.scenario_id}",
            f"Title: {scenario.title}",
            f"Notes: {scenario.notes}",
            f"Repository root: {repo_root}",
            "Rebuild commands:",
            *[f"- {command}" for command in scenario.build.rebuild_cmds],
            "Test commands:",
            *[f"- {command}" for command in scenario.build.test_cmds],
            "Target files and nearby test context:",
        ]
        for relative_path in target_files:
            file_path = repo_root / relative_path
            if not file_path.exists():
                continue
            sections.append(f"\n--- FILE: {relative_path} ---")
            sections.append(file_path.read_text(encoding="utf-8"))

        for test_path in self._discover_test_files(repo_root):
            sections.append(f"\n--- TEST: {test_path} ---")
            sections.append((repo_root / test_path).read_text(encoding="utf-8"))

        sections.append(
            "\nReturn only the patch. Do not include explanations, markdown fences, or prose."
        )
        return "\n".join(sections)

    @staticmethod
    def _build_patch_repair_prompt(
        *,
        original_prompt: str,
        invalid_patch: str,
        validation_error: str,
    ) -> str:
        return "\n".join(
            [
                "Your previous answer was not a valid unified diff patch.",
                f"Validation error: {validation_error}",
                "Return a corrected unified diff patch only.",
                "Do not include commentary, placeholders, ellipses, or omitted sections.",
                "Every hunk header must match the actual number of removed and added lines.",
                "Original task prompt:",
                original_prompt,
                "Previous invalid patch:",
                invalid_patch,
            ]
        )

    @staticmethod
    def _validate_unified_diff(patch_text: str) -> str:
        text = patch_text.strip()
        if not text:
            return "Patch is empty."
        if "omitted for brevity" in text.lower():
            return "Patch contains placeholder prose."
        lines = text.splitlines()
        has_git_header = any(line.startswith("diff --git ") for line in lines)
        has_plain_headers = any(line.startswith("--- ") for line in lines) and any(
            line.startswith("+++ ") for line in lines
        )
        if not has_git_header and not has_plain_headers:
            return "Patch does not contain recognizable diff file headers."
        if not any(line.startswith("@@") for line in lines):
            return "Patch does not contain any hunk headers."

        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.startswith("@@"):
                i += 1
                continue
            match = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            old_count = int(match.group(2) or "1") if match else None
            new_count = int(match.group(4) or "1") if match else None
            removed = 0
            added = 0
            i += 1
            while i < len(lines):
                current = lines[i]
                if current.startswith("diff --git ") or current.startswith("@@"):
                    i -= 1
                    break
                if current.startswith(("--- ", "+++ ", "index ")):
                    i += 1
                    continue
                if current.startswith("\\ No newline at end of file"):
                    i += 1
                    continue
                if current.startswith("+"):
                    added += 1
                elif current.startswith("-"):
                    removed += 1
                elif current.startswith(" "):
                    removed += 1
                    added += 1
                else:
                    return f"Unsupported diff line: {current}"
                i += 1
            if old_count is not None and new_count is not None and (
                removed != old_count or added != new_count
            ):
                return (
                    f"Hunk header count mismatch: expected -{old_count} +{new_count}, "
                    f"saw -{removed} +{added}."
                )
            i += 1
        return ""

    @staticmethod
    def _normalize_unified_diff(patch_text: str) -> str:
        text = patch_text.strip()
        if not text:
            return ""
        lines = text.splitlines()
        normalized: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.startswith("@@"):
                normalized.append(line)
                i += 1
                continue

            match = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$", line)
            if not match:
                normalized.append(line)
                i += 1
                continue

            old_start = int(match.group(1))
            new_start = int(match.group(3))
            suffix = match.group(5) or ""
            hunk_lines: list[str] = []
            i += 1
            while i < len(lines):
                current = lines[i]
                if current.startswith("diff --git ") or current.startswith("@@"):
                    break
                hunk_lines.append(current)
                i += 1

            old_count = 0
            new_count = 0
            for current in hunk_lines:
                if current.startswith("-"):
                    old_count += 1
                elif current.startswith("+"):
                    new_count += 1
                elif current.startswith(" "):
                    old_count += 1
                    new_count += 1
                elif current.startswith("\\ No newline at end of file"):
                    continue
                else:
                    normalized.append(line)
                    normalized.extend(hunk_lines)
                    break
            else:
                normalized.append(
                    f"@@ -{old_start},{old_count} +{new_start},{new_count} @@{suffix}"
                )
                normalized.extend(hunk_lines)
                continue

        return "\n".join(normalized).strip()

    @staticmethod
    def _discover_default_targets(repo_root: Path) -> list[str]:
        candidates = []
        for root_name in ("src",):
            root_dir = repo_root / root_name
            if root_dir.exists():
                for path in root_dir.rglob("*.py"):
                    candidates.append(str(path.relative_to(repo_root)).replace("\\", "/"))
        return candidates[:10]

    @staticmethod
    def _discover_test_files(repo_root: Path) -> list[str]:
        tests_dir = repo_root / "tests"
        if not tests_dir.exists():
            return []
        files = [
            str(path.relative_to(repo_root)).replace("\\", "/")
            for path in tests_dir.rglob("test_*.py")
        ]
        return files[:10]

    @staticmethod
    def _extract_patch(response_text: str) -> str:
        text = response_text.strip()
        if not text:
            return ""

        fenced_patch = OpenAICodePatchAgent._extract_fenced_patch(text)
        if fenced_patch:
            return fenced_patch

        file_block_patch = OpenAICodePatchAgent._extract_file_block_patch(text)
        if file_block_patch:
            return file_block_patch

        lines = text.splitlines()
        patch_lines: list[str] = []
        started = False
        saw_hunk = False

        for index, line in enumerate(lines):
            if not started and not OpenAICodePatchAgent._is_patch_start(lines, index):
                continue
            if not started:
                started = True

            if OpenAICodePatchAgent._looks_like_patch_line(line):
                patch_lines.append(line)
                if line.startswith("@@"):
                    saw_hunk = True
                continue

            if saw_hunk and patch_lines:
                break

        if patch_lines:
            return "\n".join(patch_lines).strip()
        return text

    @staticmethod
    def _extract_fenced_patch(text: str) -> str:
        block_pattern = re.compile(r"```(?:diff|patch)?\s*\n(.*?)```", re.DOTALL)
        for match in block_pattern.finditer(text):
            candidate = match.group(1).strip()
            if candidate and OpenAICodePatchAgent._contains_patch_markers(candidate):
                return candidate
        return ""

    @staticmethod
    def _extract_file_block_patch(text: str) -> str:
        lines = text.splitlines()
        patch_lines: list[str] = []
        found_block = False
        index = 0

        while index < len(lines):
            match = re.match(r"^--- FILE:\s+(.+?)\s+---$", lines[index].strip())
            if not match:
                index += 1
                continue

            found_block = True
            relative_path = match.group(1).strip().replace("\\", "/")
            patch_lines.append(f"--- a/{relative_path}")
            patch_lines.append(f"+++ b/{relative_path}")
            index += 1

            while index < len(lines):
                current = lines[index]
                if re.match(r"^--- FILE:\s+(.+?)\s+---$", current.strip()):
                    break
                if current.startswith("--- PATCH REPAIR ---"):
                    break
                if current.startswith("@@") or current.startswith(("+", "-", " ", "\\ No newline")):
                    patch_lines.append(current)
                index += 1

        if not found_block:
            return ""
        return "\n".join(patch_lines).strip()

    @staticmethod
    def _contains_patch_markers(text: str) -> bool:
        lines = text.splitlines()
        return any(line.startswith("@@") for line in lines) and (
            any(line.startswith("diff --git ") for line in lines)
            or (
                any(line.startswith("--- ") for line in lines)
                and any(line.startswith("+++ ") for line in lines)
            )
        )

    @staticmethod
    def _is_patch_start(lines: list[str], index: int) -> bool:
        line = lines[index]
        if line.startswith("diff --git "):
            return True
        if line.startswith("--- "):
            return index + 1 < len(lines) and lines[index + 1].startswith("+++ ")
        return False

    @staticmethod
    def _looks_like_patch_line(line: str) -> bool:
        return line.startswith(
            (
                "diff --git ",
                "index ",
                "--- ",
                "+++ ",
                "@@",
                "+",
                "-",
                " ",
                "\\ No newline at end of file",
            )
        )
