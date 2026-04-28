"""Tests for batch prediction evaluation."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from acbench.evaluation.evaluate import evaluate_predictions


class EvaluateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="acbench-eval-"))
        self.output_path = self.temp_dir / "results.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_local_gold_manifest_evaluation(self) -> None:
        results = evaluate_predictions(
            manifest_path=Path("manifests/local_suite.json"),
            predictions_path=Path("predictions/local_gold.json"),
            output_path=self.output_path,
        )

        self.assertEqual(results["submitted"], 12)
        self.assertEqual(results["success"], 12)
        self.assertTrue(self.output_path.exists())
        payload = json.loads(self.output_path.read_text(encoding="utf-8"))
        self.assertIn("code_only_billing_pricing_bundle_threshold", payload["results"])
        self.assertIn("ops_only_cache_api_stale_index", payload["results"])
        self.assertIn("combined_billing_pricing_checkout_totals", payload["results"])

    def test_prediction_defaults_can_drive_agent_runs(self) -> None:
        manifest_path = self.temp_dir / "single_scenario_manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "name": "single-code-scenario",
                    "scenarios": [
                        {
                            "scenario": "tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json"
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        predictions_path = self.temp_dir / "agent_predictions.json"
        predictions_path.write_text(
            json.dumps(
                {
                    "_defaults": {
                        "code_agent_ref": "tests.test_standalone_code_executor:FakePatchAgent",
                        "openai_model": "test-model",
                    },
                    "code_only_billing_pricing_bundle_threshold": {},
                }
            ),
            encoding="utf-8",
        )

        results = evaluate_predictions(
            manifest_path=manifest_path,
            predictions_path=predictions_path,
            output_path=self.output_path,
        )

        self.assertEqual(results["submitted"], 1)
        self.assertEqual(results["success"], 1)
        self.assertIn(
            "code_only_billing_pricing_bundle_threshold",
            results["results"],
        )

    def test_prediction_defaults_can_drive_ops_agent_runs(self) -> None:
        manifest_path = self.temp_dir / "single_ops_manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "name": "single-ops-scenario",
                    "scenarios": [
                        {
                            "scenario": "tasks/scenarios/local/ops/queue_worker__backlog_spike.scenario.json"
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        predictions_path = self.temp_dir / "agent_ops_predictions.json"
        predictions_path.write_text(
            json.dumps(
                {
                    "_defaults": {
                        "aiops_agent_ref": "tests.test_openai_ops_agent:FakeOpsAssessmentAgent",
                        "openai_model": "test-model",
                    },
                    "ops_only_queue_worker_backlog_spike": {},
                }
            ),
            encoding="utf-8",
        )

        results = evaluate_predictions(
            manifest_path=manifest_path,
            predictions_path=predictions_path,
            output_path=self.output_path,
        )

        self.assertEqual(results["submitted"], 1)
        self.assertEqual(results["success"], 1)
        self.assertEqual(
            results["results"]["ops_only_queue_worker_backlog_spike"]["ops_backend"],
            "acbench-local-ops",
        )
