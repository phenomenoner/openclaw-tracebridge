from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..io import JsonlTraceWriter
from ..schema import EventKind, TraceEvent


def _infer_kind(row: dict[str, Any]) -> EventKind:
    role = str(row.get("role", "")).lower()
    text = str(row.get("text", row.get("content", "")))
    row_type = str(row.get("type", "")).lower()

    if "heartbeat_ok" in text.lower() or row_type == "heartbeat":
        return EventKind.HEARTBEAT
    if row_type.startswith("tool") and "result" in row_type:
        return EventKind.TOOL_RESULT
    if row_type.startswith("tool"):
        return EventKind.TOOL_CALL
    if role == "user":
        return EventKind.AGENT_INPUT
    if role in {"assistant", "system"}:
        return EventKind.AGENT_OUTPUT
    return EventKind.NOTE


def _content_of(row: dict[str, Any]) -> str:
    content = row.get("text", row.get("content", ""))
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False)


def import_openclaw_session(
    session_jsonl: Path,
    out_events: Path,
    run_id: str,
    include_content: bool = False,
    start_sequence_id: int = 1,
) -> int:
    writer = JsonlTraceWriter(out_events, flush_every=200)
    seq = start_sequence_id
    count = 0

    with session_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            text = _content_of(row)
            attrs: dict[str, Any] = {
                "role": row.get("role"),
                "type": row.get("type"),
                "content_chars": len(text),
            }
            if include_content:
                attrs["content"] = text

            event = TraceEvent(
                run_id=run_id,
                sequence_id=seq,
                kind=_infer_kind(row),
                actor="openclaw",
                attrs=attrs,
                token_estimate=max(1, len(text) // 4) if text else 0,
                prompt_chars=len(text) if str(row.get("role", "")).lower() == "user" else None,
                response_chars=len(text) if str(row.get("role", "")).lower() in {"assistant", "system"} else None,
            )
            writer.append(event)
            seq += 1
            count += 1

    writer.close()
    return count
