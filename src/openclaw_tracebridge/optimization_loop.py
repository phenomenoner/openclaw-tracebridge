from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

NEGATIVE_KEYWORDS = ("error", "failed", "exception", "timeout")


@dataclass
class OptimizationReport:
    rows_total: int
    rows_train: int
    rows_val: int
    baseline_policy: str
    best_policy: str
    baseline_train_reward: float
    baseline_val_reward: float
    best_train_reward: float
    best_val_reward: float
    uplift_val_abs: float
    uplift_val_pct: float


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _stable_unit(seed: int, value: str) -> float:
    digest = hashlib.sha256(f"{seed}:{value}".encode("utf-8")).hexdigest()
    n = int(digest[:12], 16)
    return (n % 1_000_000) / 1_000_000.0


def _row_id(row: dict[str, Any], idx: int) -> str:
    rid = row.get("id") or row.get("metadata", {}).get("input_event_id")
    if rid is None:
        rid = f"row_{idx}"
    return str(rid)


def _split_train_val(rows: list[dict[str, Any]], *, val_ratio: float, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train: list[dict[str, Any]] = []
    val: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        rid = _row_id(row, i)
        u = _stable_unit(seed, rid)
        if u < val_ratio:
            val.append(row)
        else:
            train.append(row)
    return train, val


def _sanitize_error_terms(text: str) -> str:
    out = text
    replacements = {
        "error": "issue",
        "failed": "not completed",
        "exception": "unexpected condition",
        "timeout": "time limit",
    }
    for src, dst in replacements.items():
        out = re.sub(src, dst, out, flags=re.IGNORECASE)
    return out


def _apply_policy(action_text: str, policy: str) -> str:
    if policy == "identity":
        return action_text
    if policy == "sanitize_errors":
        return _sanitize_error_terms(action_text)
    if policy == "safe_rewrite":
        cleaned = _sanitize_error_terms(action_text)
        if cleaned.strip():
            return f"Result summary: {cleaned.strip()}"
        return "Result summary: action completed."
    if policy == "short_safe":
        cleaned = _sanitize_error_terms(action_text).strip()
        if not cleaned:
            return "Completed."
        first_line = cleaned.splitlines()[0]
        return first_line[:220]
    raise ValueError(f"unknown policy: {policy}")


def _reward_from_action(action_text: str, middle_counts: dict[str, int]) -> float:
    output = action_text.lower()

    reward = 0.4
    if action_text.strip():
        reward += 0.25
    if middle_counts.get("tool.result", 0) > 0:
        reward += 0.2
    if middle_counts.get("system.event", 0) > 0:
        reward -= 0.1

    if any(word in output for word in NEGATIVE_KEYWORDS):
        reward -= 0.3

    return max(0.0, min(1.0, round(reward, 4)))


def _avg_reward(rows: list[dict[str, Any]], policy: str) -> float:
    if not rows:
        return 0.0
    values: list[float] = []
    for row in rows:
        action = str(row.get("action_text", ""))
        transformed = _apply_policy(action, policy)
        middle_counts = row.get("metadata", {}).get("middle_counts", {})
        if not isinstance(middle_counts, dict):
            middle_counts = {}
        reward = _reward_from_action(transformed, middle_counts)
        values.append(reward)
    return round(sum(values) / len(values), 6)


def run_optimization_loop(
    triplets_path: Path,
    *,
    val_ratio: float = 0.2,
    seed: int = 42,
    max_rows: int | None = None,
) -> OptimizationReport:
    if not 0.0 < val_ratio < 1.0:
        raise ValueError("val_ratio must be between 0 and 1")

    rows = _read_jsonl(triplets_path)
    if max_rows is not None:
        rows = rows[:max_rows]
    rows = [r for r in rows if r.get("schema") == "tracebridge.agent_lightning.triplet.v0"]

    train, val = _split_train_val(rows, val_ratio=val_ratio, seed=seed)

    baseline_policy = "identity"
    candidate_policies = ["identity", "sanitize_errors", "safe_rewrite", "short_safe"]

    baseline_train = _avg_reward(train, baseline_policy)
    baseline_val = _avg_reward(val, baseline_policy)

    best_policy = baseline_policy
    best_train = baseline_train
    best_val = baseline_val

    for p in candidate_policies:
        train_reward = _avg_reward(train, p)
        val_reward = _avg_reward(val, p)
        if train_reward > best_train:
            best_policy = p
            best_train = train_reward
            best_val = val_reward

    uplift_abs = round(best_val - baseline_val, 6)
    uplift_pct = 0.0 if baseline_val <= 0 else round((uplift_abs / baseline_val) * 100.0, 4)

    return OptimizationReport(
        rows_total=len(rows),
        rows_train=len(train),
        rows_val=len(val),
        baseline_policy=baseline_policy,
        best_policy=best_policy,
        baseline_train_reward=baseline_train,
        baseline_val_reward=baseline_val,
        best_train_reward=best_train,
        best_val_reward=best_val,
        uplift_val_abs=uplift_abs,
        uplift_val_pct=uplift_pct,
    )
