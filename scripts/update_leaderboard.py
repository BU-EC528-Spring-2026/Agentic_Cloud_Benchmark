#!/usr/bin/env python3
"""Update the static website leaderboard from ACBench evaluation JSON files."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


MODE_TO_FIELD = {
    "code_only": "code",
    "ops_only": "ops",
    "combined": "combined",
}


def _normalize_score(score: float) -> float:
    """Return a percentage score, accepting either 0..1 or 0..100 inputs."""

    return score * 100.0 if score <= 1.0 else score


def summarize_evaluations(eval_paths: list[Path]) -> dict[str, float | int]:
    """Summarize one or more evaluation outputs into leaderboard fields."""

    scores_by_mode: dict[str, list[float]] = defaultdict(list)
    scenarios = 0

    for eval_path in eval_paths:
        payload = json.loads(eval_path.read_text(encoding="utf-8"))
        results = payload.get("results", {})
        if isinstance(results, dict) and results:
            scenarios += len(results)
            for item in results.values():
                mode = str(item.get("mode", ""))
                field = MODE_TO_FIELD.get(mode)
                if not field:
                    continue
                scores_by_mode[field].append(
                    _normalize_score(float(item.get("final_score", 0.0)))
                )
        else:
            scenarios += int(payload.get("submitted", 0))

    summary: dict[str, float | int] = {"scenarios": scenarios}
    for field in ("code", "ops", "combined"):
        values = scores_by_mode[field]
        summary[field] = round(sum(values) / len(values), 1) if values else 0.0
    return summary


def _extract_rows(js_text: str) -> list[dict[str, Any]]:
    match = re.search(
        r"const\s+leaderboardRows\s*=\s*(\[.*?\]);",
        js_text,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError("Could not find `const leaderboardRows = [...]`.")

    array_text = match.group(1)
    json_text = re.sub(
        r"(\s*)(agent|model|code|ops|combined|scenarios)(\s*):",
        r'\1"\2"\3:',
        array_text,
    )
    return json.loads(json_text)


def _format_rows(rows: list[dict[str, Any]]) -> str:
    return "const leaderboardRows = " + json.dumps(rows, indent=2) + ";"


def update_leaderboard(
    *,
    website_js: Path,
    agent: str,
    model: str,
    eval_paths: list[Path],
) -> dict[str, Any]:
    js_text = website_js.read_text(encoding="utf-8")
    rows = _extract_rows(js_text)
    summary = summarize_evaluations(eval_paths)
    new_row: dict[str, Any] = {
        "agent": agent,
        "model": model,
        "code": summary["code"],
        "ops": summary["ops"],
        "combined": summary["combined"],
        "scenarios": str(summary["scenarios"]),
    }

    replaced = False
    for index, row in enumerate(rows):
        if row.get("agent") == agent:
            rows[index] = new_row
            replaced = True
            break
    if not replaced:
        rows.append(new_row)

    updated_text = re.sub(
        r"const\s+leaderboardRows\s*=\s*\[.*?\];",
        _format_rows(rows),
        js_text,
        count=1,
        flags=re.DOTALL,
    )
    website_js.write_text(updated_text, encoding="utf-8")
    return new_row


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update website/main.js from ACBench evaluation JSON files."
    )
    parser.add_argument("--agent", required=True, help="Display name for the agent.")
    parser.add_argument("--model", required=True, help="Display model name.")
    parser.add_argument(
        "--eval",
        action="append",
        required=True,
        dest="eval_paths",
        help="Evaluation JSON path. Pass once per suite, e.g. local and GitHub.",
    )
    parser.add_argument(
        "--website-js",
        default="website/main.js",
        help="Path to the static website JavaScript file.",
    )
    args = parser.parse_args()

    row = update_leaderboard(
        website_js=Path(args.website_js),
        agent=args.agent,
        model=args.model,
        eval_paths=[Path(path) for path in args.eval_paths],
    )
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
