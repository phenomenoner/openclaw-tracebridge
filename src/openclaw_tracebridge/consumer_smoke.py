from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ConsumerSmokeSummary:
    format: str
    rows_total: int
    rows_ok: int
    rows_bad: int
    sample_ids: list[str]
    avg_user_chars: float | None = None
    avg_assistant_chars: float | None = None
    avg_state_chars: float | None = None
    avg_action_chars: float | None = None


def _iter_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def smoke_check_messages(path: Path, max_rows: int | None = None) -> ConsumerSmokeSummary:
    rows = _iter_jsonl(path)
    if max_rows is not None:
        rows = rows[:max_rows]

    ok = 0
    bad = 0
    sample_ids: list[str] = []
    user_chars: list[int] = []
    assistant_chars: list[int] = []

    for row in rows:
        schema = row.get("schema")
        rid = str(row.get("id", ""))
        messages = row.get("messages")

        row_ok = True
        if schema != "tracebridge.agent_lightning.messages.v0":
            row_ok = False
        if not isinstance(messages, list) or len(messages) < 2:
            row_ok = False
        else:
            first = messages[0]
            second = messages[1]
            if first.get("role") != "user" or second.get("role") != "assistant":
                row_ok = False
            user_text = first.get("content")
            assistant_text = second.get("content")
            if not isinstance(user_text, str) or not user_text.strip():
                row_ok = False
            if not isinstance(assistant_text, str) or not assistant_text.strip():
                row_ok = False

            if row_ok:
                user_chars.append(len(user_text))
                assistant_chars.append(len(assistant_text))

        if row_ok:
            ok += 1
            if len(sample_ids) < 5 and rid:
                sample_ids.append(rid)
        else:
            bad += 1

    avg_user = (sum(user_chars) / len(user_chars)) if user_chars else None
    avg_assistant = (sum(assistant_chars) / len(assistant_chars)) if assistant_chars else None

    return ConsumerSmokeSummary(
        format="messages",
        rows_total=len(rows),
        rows_ok=ok,
        rows_bad=bad,
        sample_ids=sample_ids,
        avg_user_chars=round(avg_user, 2) if avg_user is not None else None,
        avg_assistant_chars=round(avg_assistant, 2) if avg_assistant is not None else None,
    )


def smoke_check_triplets(path: Path, max_rows: int | None = None) -> ConsumerSmokeSummary:
    rows = _iter_jsonl(path)
    if max_rows is not None:
        rows = rows[:max_rows]

    ok = 0
    bad = 0
    sample_ids: list[str] = []
    state_chars: list[int] = []
    action_chars: list[int] = []

    for row in rows:
        schema = row.get("schema")
        rid = str(row.get("id", ""))
        state_text = row.get("state_text")
        action_text = row.get("action_text")
        reward = row.get("reward")

        row_ok = True
        if schema != "tracebridge.agent_lightning.triplet.v0":
            row_ok = False
        if not isinstance(state_text, str) or not state_text.strip():
            row_ok = False
        if not isinstance(action_text, str) or not action_text.strip():
            row_ok = False
        if reward is not None and not isinstance(reward, (int, float)):
            row_ok = False

        if row_ok:
            ok += 1
            state_chars.append(len(state_text))
            action_chars.append(len(action_text))
            if len(sample_ids) < 5 and rid:
                sample_ids.append(rid)
        else:
            bad += 1

    avg_state = (sum(state_chars) / len(state_chars)) if state_chars else None
    avg_action = (sum(action_chars) / len(action_chars)) if action_chars else None

    return ConsumerSmokeSummary(
        format="triplets",
        rows_total=len(rows),
        rows_ok=ok,
        rows_bad=bad,
        sample_ids=sample_ids,
        avg_state_chars=round(avg_state, 2) if avg_state is not None else None,
        avg_action_chars=round(avg_action, 2) if avg_action is not None else None,
    )
