"""Basic tests for the ACBench prototype skeleton."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import json

from acbench.executors.base import BenchmarkExecutor
from acbench.executors.local_code import LocalCodeExecutor
from acbench.executors.standalone_code import StandaloneCodeExecutor
from acbench.models.result import ExecutorResult
from acbench.models.runtime import RunConfig
from acbench.models.scenario import ScenarioSpec
from acbench.runner import ACBenchRunner


class ScenarioModelTests(unittest.TestCase):
    def test_combined_requires_both_faults(self) -> None:
        with self.assertRaises(ValueError):
            ScenarioSpec.from_dict(
                {
                    "scenario_id": "bad-combined",
                    "title": "bad",
                    "mode": "combined",
                    "service": {
                        "application": "app",
                        "service": "svc",
                    },
                    "build": {
                        "test_cmds": ["pytest"],
                    },
                }
            )


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="acbench-test-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dry_run_combined_scenario_writes_result(self) -> None:
        runner = ACBenchRunner(root_dir=self.temp_dir)
        scenario_path = (
            Path(__file__).resolve().parents[1]
            / "standalone"
            / "scenarios"
            / "combined"
            / "samplepkg__local_fixture.scenario.json"
        )

        result = runner.run(scenario_path, dry_run=True)

        self.assertEqual(result.status, "success")
        self.assertIsNotNone(result.ops_result)
        self.assertTrue(Path(result.artifacts.result_path).exists())
        self.assertTrue(Path(result.artifacts.summary_path).exists())
        self.assertTrue(Path(result.artifacts.scenario_path).exists())
        self.assertTrue(Path(result.artifacts.diagnostics_path).exists())
    def test_live_run_is_blocked_when_environment_is_not_ready(self) -> None:
        runner = ACBenchRunner(root_dir=self.temp_dir)
        scenario_path = (
            Path(__file__).resolve().parents[1]
            / "standalone"
            / "scenarios"
            / "combined"
            / "samplepkg__local_fixture.scenario.json"
        )

        class FakeIssue:
            source = "test"
            message = "synthetic readiness failure"

        class FakeReadiness:
            ready_for_live_run = False
            issues = [FakeIssue()]

            @staticmethod
            def to_dict() -> dict:
                return {
                    "ready_for_live_run": False,
                    "issues": [{"source": "test", "message": "synthetic readiness failure"}],
                }

        with patch("acbench.runner.check_scenario_readiness", return_value=FakeReadiness()):
            with self.assertRaises(RuntimeError):
                runner.run(scenario_path, dry_run=False)

    def test_executor_failure_is_captured_into_result_artifacts(self) -> None:
        runner = ACBenchRunner(root_dir=self.temp_dir)
        scenario_path = (
            Path(__file__).resolve().parents[1]
            / "standalone"
            / "scenarios"
            / "code"
            / "samplepkg__local_repo_buggy.scenario.json"
        )

        class FailingExecutor(BenchmarkExecutor):
            def __init__(self) -> None:
                super().__init__(backend_name="failing-code")

            def execute(self, scenario, run_dir, run_config) -> ExecutorResult:
                raise RuntimeError("synthetic executor failure")

        with patch.object(
            ACBenchRunner,
            "select_code_executor",
            return_value=FailingExecutor(),
        ):
            result = runner.run(
                scenario_path,
                dry_run=False,
                run_config=RunConfig(dry_run=False),
            )

        self.assertEqual(result.status, "failed")
        self.assertIsNotNone(result.code_result)
        self.assertEqual(result.code_result.backend, "failing-code")
        self.assertFalse(result.code_result.success)
        self.assertIn("synthetic executor failure", result.notes[0])
        self.assertTrue(Path(result.artifacts.result_path).exists())
        self.assertTrue(Path(result.artifacts.summary_path).exists())
        exception_path = Path(result.code_result.logs["exception_path"])
        self.assertTrue(exception_path.exists())
        self.assertIn("synthetic executor failure", exception_path.read_text(encoding="utf-8"))

    def test_code_summary_contains_code_specific_fields(self) -> None:
        runner = ACBenchRunner(root_dir=self.temp_dir)
        scenario_path = (
            Path(__file__).resolve().parents[1]
            / "standalone"
            / "scenarios"
            / "code"
            / "samplepkg__local_repo_buggy.scenario.json"
        )

        result = runner.run(
            scenario_path,
            dry_run=False,
            run_config=RunConfig(
                dry_run=False,
                code_patch_path=str(
                    Path(__file__).resolve().parents[1]
                    / "patches"
                    / "local_repo_buggy_fix.diff"
                ),
            ),
        )

        summary = Path(result.artifacts.summary_path).read_text(encoding="utf-8")
        self.assertIn("\"submitted_instance_id\"", summary)
        self.assertIn("\"resolved\"", summary)

    def test_local_combined_promotes_ops_trace_artifacts(self) -> None:
        runner = ACBenchRunner(root_dir=self.temp_dir)
        scenario_path = (
            Path(__file__).resolve().parents[1]
            / "standalone"
            / "scenarios"
            / "combined"
            / "samplepkg__local_fixture.scenario.json"
        )
        patch_path = (
            Path(__file__).resolve().parents[1]
            / "patches"
            / "local_repo_buggy_fix.diff"
        )

        result = runner.run(
            scenario_path,
            dry_run=False,
            run_config=RunConfig(
                dry_run=False,
                code_patch_path=str(patch_path),
                max_steps=5,
            ),
        )

        self.assertTrue(Path(result.artifacts.trace_path).exists())
        self.assertTrue(Path(result.artifacts.telemetry_summary_path).exists())

    def test_acbench_local_code_executor_can_use_agent_generated_patch(self) -> None:
        runner = ACBenchRunner(root_dir=self.temp_dir)
        scenario_path = (
            Path(__file__).resolve().parents[1]
            / "standalone"
            / "scenarios"
            / "code"
            / "samplepkg__local_repo_buggy.scenario.json"
        )

        executor = runner.select_code_executor(
            ScenarioSpec.from_file(scenario_path),
            dry_run=False,
        )
        self.assertIsInstance(executor, LocalCodeExecutor)

        result = runner.run(
            scenario_path,
            dry_run=False,
            run_config=RunConfig(
                dry_run=False,
                code_agent_ref="acbench.tests.test_standalone_code_executor:FakePatchAgent",
                openai_model="test-model",
            ),
        )

        self.assertEqual(result.code_result.backend, "acbench-local-code")
        self.assertTrue(result.code_result.success)
        self.assertTrue(Path(result.code_result.details["code_patch_path"]).exists())


if __name__ == "__main__":
    unittest.main()
