from __future__ import annotations

import json

from scripts.update_leaderboard import summarize_evaluations, update_leaderboard


def test_summarize_evaluations_groups_scores_by_mode(tmp_path):
    eval_path = tmp_path / "eval.json"
    eval_path.write_text(
        json.dumps(
            {
                "results": {
                    "code-a": {"mode": "code_only", "final_score": 1.0},
                    "code-b": {"mode": "code_only", "final_score": 0.5},
                    "ops-a": {"mode": "ops_only", "final_score": 75.0},
                    "combined-a": {"mode": "combined", "final_score": 0.25},
                }
            }
        ),
        encoding="utf-8",
    )

    assert summarize_evaluations([eval_path]) == {
        "scenarios": 4,
        "code": 75.0,
        "ops": 75.0,
        "combined": 25.0,
    }


def test_update_leaderboard_replaces_matching_agent(tmp_path):
    website_js = tmp_path / "main.js"
    website_js.write_text(
        """const leaderboardRows = [
  {
    agent: "Agent A",
    model: "old",
    code: 0,
    ops: 0,
    combined: 0,
    scenarios: "0"
  }
];

function noop() {}
""",
        encoding="utf-8",
    )
    eval_path = tmp_path / "eval.json"
    eval_path.write_text(
        json.dumps({"results": {"code-a": {"mode": "code_only", "final_score": 1.0}}}),
        encoding="utf-8",
    )

    row = update_leaderboard(
        website_js=website_js,
        agent="Agent A",
        model="new",
        eval_paths=[eval_path],
    )

    assert row["code"] == 100.0
    assert row["scenarios"] == "1"
    text = website_js.read_text(encoding="utf-8")
    assert '"model": "new"' in text
    assert "function noop() {}" in text
