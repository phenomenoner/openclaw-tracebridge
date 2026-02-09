from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ReplaySplitSummary:
    input_rows: int
    sampled_rows: int
    out_a_rows: int
    out_b_rows: int


def _hash_to_unit(value: str) -> float:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    bucket = int(digest[:12], 16)
    return (bucket % 1_000_000) / 1_000_000.0


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _stable_key(row: dict[str, Any], key_field: str, idx: int) -> str:
    key = row.get(key_field)
    if key is None:
        key = row.get("event_id") or row.get("id") or row.get("sequence_id")
    if key is None:
        key = idx
    return str(key)


def split_jsonl_for_replay(
    input_path: Path,
    out_a_path: Path,
    out_b_path: Path,
    *,
    split_ratio: float = 0.5,
    seed: int = 42,
    key_field: str = "id",
    sample_size: int | None = None,
    sample_seed: int = 42,
) -> ReplaySplitSummary:
    if not 0 < split_ratio < 1:
        raise ValueError("split_ratio must be between 0 and 1")

    rows = _read_jsonl(input_path)

    if sample_size is not None:
        scored: list[tuple[float, dict[str, Any]]] = []
        for idx, row in enumerate(rows):
            key = _stable_key(row, key_field=key_field, idx=idx)
            s = _hash_to_unit(f"sample:{sample_seed}:{key}")
            scored.append((s, row))
        sampled_rows = [row for _, row in sorted(scored, key=lambda t: t[0])[:sample_size]]
    else:
        sampled_rows = rows

    out_a: list[dict[str, Any]] = []
    out_b: list[dict[str, Any]] = []

    for idx, row in enumerate(sampled_rows):
        key = _stable_key(row, key_field=key_field, idx=idx)
        score = _hash_to_unit(f"split:{seed}:{key}")
        if score < split_ratio:
            out_a.append(row)
        else:
            out_b.append(row)

    _write_jsonl(out_a_path, out_a)
    _write_jsonl(out_b_path, out_b)

    return ReplaySplitSummary(
        input_rows=len(rows),
        sampled_rows=len(sampled_rows),
        out_a_rows=len(out_a),
        out_b_rows=len(out_b),
    )


def build_replay_manifest(input_path: Path) -> dict[str, Any]:
    payload = input_path.read_bytes()
    rows = _read_jsonl(input_path)
    return {
        "schema": "tracebridge.replay.manifest.v0",
        "input": str(input_path),
        "rows": len(rows),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
