"""Tests for the OpenAI-backed code patch agent."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from acbench.agents.openai_code import OpenAICodePatchAgent
from acbench.models.runtime import RunConfig
from acbench.models.scenario import ScenarioSpec


class _FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class _FakeClient:
    def __init__(self, output_text: str | list[str]) -> None:
        if isinstance(output_text, list):
            self._output_texts = output_text
        else:
            self._output_texts = [output_text]
        self.responses = self
        self.last_create_kwargs: dict[str, str] = {}
        self.calls: list[dict[str, str]] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        self.last_create_kwargs = kwargs
        index = min(len(self.calls) - 1, len(self._output_texts) - 1)
        return _FakeResponse(self._output_texts[index])


class OpenAICodePatchAgentTests(unittest.TestCase):
    def test_build_prompt_uses_repository_context_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir) / "repo"
            src_dir = repo_root / "src"
            tests_dir = repo_root / "tests"
            src_dir.mkdir(parents=True)
            tests_dir.mkdir(parents=True)
            (src_dir / "main.py").write_text("print('buggy')\n", encoding="utf-8")
            (tests_dir / "test_main.py").write_text("def test_ok(): pass\n", encoding="utf-8")

            scenario = ScenarioSpec.from_dict(
                {
                    "scenario_id": "local-code",
                    "title": "local",
                    "mode": "code_only",
                    "service": {
                        "application": "app",
                        "service": "svc",
                        "repository_path": str(repo_root),
                    },
                    "code_fault": {
                        "source": "acbench",
                        "defect_id": "d1",
                        "target_files": ["src/main.py"],
                    },
                    "build": {
                        "rebuild_cmds": ["python -m compileall ."],
                        "test_cmds": ["python -m unittest"],
                    },
                }
            )

            prompt = OpenAICodePatchAgent()._build_prompt(scenario)

            self.assertIn("Repository root:", prompt)
            self.assertIn("--- FILE: src/main.py ---", prompt)
            self.assertIn("print('buggy')", prompt)

    def test_build_prompt_uses_native_instance_without_leaking_gold_patch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            instance_path = Path(tmp_dir) / "instance.json"
            instance_path.write_text(
                json.dumps(
                    {
                        "instance_id": "native-1",
                        "repo": "owner/repo",
                        "base_commit": "abc123",
                        "patch": "SECRET_GOLD_PATCH",
                        "problem_statement": "The current behavior is incorrect.",
                        "hints_text": "Focus on parser scope.",
                        "PASS_TO_PASS": ["already::green"],
                        "FAIL_TO_PASS": ["scope::regression"],
                        "test_patch": "diff --git a/tests/scope.rs b/tests/scope.rs\n",
                        "commit_urls": ["https://example.invalid/commit/1"],
                        "rebuild_cmds": ["cargo build"],
                        "test_cmds": ["cargo test"],
                        "print_cmds": ["cat test-output.log"],
                    }
                ),
                encoding="utf-8",
            )
            scenario = ScenarioSpec.from_dict(
                {
                    "scenario_id": "native-code",
                    "title": "native",
                    "mode": "code_only",
                    "service": {
                        "application": "swe-bench-live",
                        "service": "svc",
                    },
                    "code_fault": {
                        "source": "swe-bench-live",
                        "defect_id": "d1",
                        "instance_path": str(instance_path),
                        "platform": "linux",
                    },
                }
            )

            prompt = OpenAICodePatchAgent()._build_prompt(scenario)

            self.assertIn("native SWE-bench benchmark task", prompt)
            self.assertIn("owner/repo", prompt)
            self.assertIn("The current behavior is incorrect.", prompt)
            self.assertIn("scope::regression", prompt)
            self.assertIn("tests/scope.rs", prompt)
            self.assertIn("https://example.invalid/commit/1", prompt)
            self.assertIn("Do not invent files, symbols, or APIs", prompt)
            self.assertNotIn("SECRET_GOLD_PATCH", prompt)

    def test_select_relevant_tests_prioritizes_keyword_matches(self) -> None:
        tests = [
            "scope::regression",
            "imports::module_context",
            "misc::unrelated_case",
        ]

        selected = OpenAICodePatchAgent._select_relevant_tests(
            tests,
            "Imported recipes use the wrong module scope.",
            "This is a scope bug in imported module context.",
        )

        self.assertIn("scope::regression", selected)
        self.assertIn("imports::module_context", selected)
        self.assertNotIn("misc::unrelated_case", selected)

    def test_generate_patch_supports_native_instance_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            instance_path = Path(tmp_dir) / "instance.json"
            output_dir = Path(tmp_dir) / "out"
            output_dir.mkdir()
            instance_path.write_text(
                json.dumps(
                    {
                        "instance_id": "native-1",
                        "repo": "owner/repo",
                        "base_commit": "abc123",
                        "problem_statement": "Fix the failing test.",
                        "hints_text": "",
                        "PASS_TO_PASS": [],
                        "FAIL_TO_PASS": ["scope::regression"],
                        "rebuild_cmds": ["cargo build"],
                        "test_cmds": ["cargo test"],
                    }
                ),
                encoding="utf-8",
            )
            scenario = ScenarioSpec.from_dict(
                {
                    "scenario_id": "native-code",
                    "title": "native",
                    "mode": "code_only",
                    "service": {
                        "application": "swe-bench-live",
                        "service": "svc",
                    },
                    "code_fault": {
                        "source": "swe-bench-live",
                        "defect_id": "d1",
                        "instance_path": str(instance_path),
                        "platform": "linux",
                    },
                }
            )
            fake_client = _FakeClient("```diff\ndiff --git a/x b/x\n@@ -1,1 +1,1 @@\n-old\n+new\n```")

            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                with patch("acbench.agents.openai_code.OpenAI", return_value=fake_client):
                    artifacts = OpenAICodePatchAgent().generate_patch(
                        scenario,
                        RunConfig(openai_model="gpt-test"),
                        output_dir=output_dir,
                    )

            self.assertEqual(artifacts["patch_text"], "diff --git a/x b/x\n@@ -1,1 +1,1 @@\n-old\n+new")
            self.assertTrue(Path(artifacts["generated_patch_path"]).exists())
            self.assertIn("Fix the failing test.", Path(artifacts["prompt_path"]).read_text(encoding="utf-8"))

    def test_generate_patch_retries_when_initial_diff_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            instance_path = Path(tmp_dir) / "instance.json"
            output_dir = Path(tmp_dir) / "out"
            output_dir.mkdir()
            instance_path.write_text(
                json.dumps(
                    {
                        "instance_id": "native-1",
                        "repo": "owner/repo",
                        "base_commit": "abc123",
                        "problem_statement": "Fix the failing test.",
                        "hints_text": "Scope issue.",
                        "PASS_TO_PASS": [],
                        "FAIL_TO_PASS": ["scope::regression"],
                        "rebuild_cmds": ["cargo build"],
                        "test_cmds": ["cargo test"],
                    }
                ),
                encoding="utf-8",
            )
            scenario = ScenarioSpec.from_dict(
                {
                    "scenario_id": "native-code",
                    "title": "native",
                    "mode": "code_only",
                    "service": {
                        "application": "swe-bench-live",
                        "service": "svc",
                    },
                    "code_fault": {
                        "source": "swe-bench-live",
                        "defect_id": "d1",
                        "instance_path": str(instance_path),
                        "platform": "linux",
                    },
                }
            )
            fake_client = _FakeClient(
                [
                    "```diff\ndiff --git a/x b/x\n@@ -1,1 +1,1 @@\n-old\n+new\nomitted for brevity\n```",
                    "```diff\ndiff --git a/x b/x\n@@ -1,1 +1,1 @@\n-old\n+new\n```",
                ]
            )

            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                with patch("acbench.agents.openai_code.OpenAI", return_value=fake_client):
                    artifacts = OpenAICodePatchAgent().generate_patch(
                        scenario,
                        RunConfig(openai_model="gpt-test"),
                        output_dir=output_dir,
                    )

            self.assertEqual(artifacts["patch_text"], "diff --git a/x b/x\n@@ -1,1 +1,1 @@\n-old\n+new")
            self.assertEqual(len(fake_client.calls), 2)
            self.assertIn("Validation error", fake_client.calls[1]["input"])

    def test_generate_patch_raises_if_diff_remains_invalid_after_retries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            instance_path = Path(tmp_dir) / "instance.json"
            output_dir = Path(tmp_dir) / "out"
            output_dir.mkdir()
            instance_path.write_text(
                json.dumps(
                    {
                        "instance_id": "native-1",
                        "repo": "owner/repo",
                        "base_commit": "abc123",
                        "problem_statement": "Fix the failing test.",
                        "hints_text": "Scope issue.",
                        "PASS_TO_PASS": [],
                        "FAIL_TO_PASS": ["scope::regression"],
                        "rebuild_cmds": ["cargo build"],
                        "test_cmds": ["cargo test"],
                    }
                ),
                encoding="utf-8",
            )
            scenario = ScenarioSpec.from_dict(
                {
                    "scenario_id": "native-code",
                    "title": "native",
                    "mode": "code_only",
                    "service": {
                        "application": "swe-bench-live",
                        "service": "svc",
                    },
                    "code_fault": {
                        "source": "swe-bench-live",
                        "defect_id": "d1",
                        "instance_path": str(instance_path),
                        "platform": "linux",
                    },
                }
            )
            fake_client = _FakeClient(
                ["```diff\ndiff --git a/x b/x\n@@ -1,1 +1,1 @@\n-old\n+new\nomitted for brevity\n```"] * 4
            )

            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
                with patch("acbench.agents.openai_code.OpenAI", return_value=fake_client):
                    with self.assertRaisesRegex(ValueError, "invalid unified diff"):
                        OpenAICodePatchAgent().generate_patch(
                            scenario,
                            RunConfig(openai_model="gpt-test"),
                            output_dir=output_dir,
                        )

            self.assertEqual(len(fake_client.calls), 4)

    def test_validate_unified_diff_rejects_placeholder_and_bad_hunk_counts(self) -> None:
        self.assertTrue(
            OpenAICodePatchAgent._validate_unified_diff("omitted for brevity")
        )
        self.assertIn(
            "Hunk header count mismatch",
            OpenAICodePatchAgent._validate_unified_diff(
                "diff --git a/x b/x\n@@ -1,1 +1,1 @@\n-old\n+new\n+extra"
            ),
        )

    def test_normalize_unified_diff_repairs_hunk_counts(self) -> None:
        normalized = OpenAICodePatchAgent._normalize_unified_diff(
            "diff --git a/x b/x\n@@ -10,7 +10,18 @@\n a\n-old\n+new\n b"
        )

        self.assertIn("@@ -10,3 +10,3 @@", normalized)
        self.assertEqual(OpenAICodePatchAgent._validate_unified_diff(normalized), "")


if __name__ == "__main__":
    unittest.main()
