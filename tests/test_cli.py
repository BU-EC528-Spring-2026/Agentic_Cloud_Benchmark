"""Tests for CLI utility output contracts."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from acbench.orchestrator.cli import build_parser, run_doctor


class CLITests(unittest.TestCase):
    def test_parser_accepts_aiops_agent_ref(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--scenario",
                "tasks/scenarios/local/combined/billing_pricing__checkout_totals_incident.scenario.json",
                "--aiops-agent-ref",
                "acbench.agents.openai_ops:OpenAIOpsAgent",
            ]
        )

        self.assertEqual(
            args.aiops_agent_ref,
            "acbench.agents.openai_ops:OpenAIOpsAgent",
        )

    def test_run_doctor_reports_standalone_backend(self) -> None:
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = run_doctor()

        payload = json.loads(stream.getvalue())
        self.assertEqual(result, 0)
        self.assertIn("acbench_code", payload)
        self.assertEqual(
            payload["acbench_code"]["extra_checks"]["backend_type"],
            "standalone-local-code",
        )


if __name__ == "__main__":
    unittest.main()
