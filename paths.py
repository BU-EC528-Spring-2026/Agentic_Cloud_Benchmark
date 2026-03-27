"""Helpers for resolving repository-local paths across package layouts."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return the repository root for the in-repo package layout."""

    return Path(__file__).resolve().parent


def resolve_repo_path(path: str | Path, *, base_dir: str | Path | None = None) -> Path:
    """Resolve a repository-local path and tolerate a legacy ``acbench/`` prefix."""

    candidate = Path(path)
    if candidate.is_absolute():
        return candidate

    base = Path(base_dir) if base_dir else Path.cwd()
    candidates = [base / candidate, repo_root() / candidate]

    if candidate.parts and candidate.parts[0] == "acbench" and len(candidate.parts) > 1:
        stripped = Path(*candidate.parts[1:])
        candidates.extend([base / stripped, repo_root() / stripped])

    for resolved in candidates:
        if resolved.exists():
            return resolved.resolve()

    return candidates[0]
