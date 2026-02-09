from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..io import JsonlTraceWriter
from ..schema import EventKind, TraceEvent


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        chunks: list[str] = []
        for item in value:
            if isinstance(item, str):
                chunks.append(item)
                continue
            if not isinstance(item, dict):
                chunks.append(json.dumps(item, ensure_ascii=False))
                continue

            item_type = str(item.get("type", "")).lower()
            if item_type in {"text", "thinking"}:
                chunks.append(str(item.get("text", item.get("thinking", ""))))
            elif "text" in item:
                chunks.append(str(item.get("text", "")))
            else:
                chunks.append(json.dumps(item, ensure_ascii=False))
        return "\n".join(filter(None, chunks))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _extract_tool_calls(content: Any) -> list[str]:
    if not isinstance(content, list):
        return []
    names: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type", "")).lower()
        if item_type == "toolcall" and item.get("name"):
            names.append(str(item["name"]))
    return names


def _extract_openclaw_fields(row: dict[str, Any]) -> tuple[str, str, dict[str, Any], list[str]]:
    row_type = str(row.get("type", "")).lower()

    # Most OpenClaw session rows are nested under row["message"] for type=message.
    if row_type == "message" and isinstance(row.get("message"), dict):
        msg = row["message"]
        role = str(msg.get("role", "")).lower()
        content = msg.get("content")
        content_text = _as_text(content)
        usage = msg.get("usage") if isinstance(msg.get("usage"), dict) else {}
        tool_calls = _extract_tool_calls(content)
        return role, content_text, usage, tool_calls

    role = str(row.get("role", "")).lower()
    text = _as_text(row.get("text", row.get("content", row.get("summary", ""))))
    return role, text, {}, []


def _looks_like_system_text(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("System:") or stripped.startswith("Note:")


def _looks_like_cron_text(text: str) -> bool:
    lower = text.lower()
    return "cron:" in lower or lower.startswith("cron:")


def _infer_kind(row: dict[str, Any], role: str, text: str, tool_calls: list[str]) -> EventKind:
    row_type = str(row.get("type", "")).lower()
    lower_text = text.lower()

    if "heartbeat_ok" in lower_text or row_type == "heartbeat":
        return EventKind.HEARTBEAT

    if row_type == "session":
        return EventKind.SYSTEM_EVENT

    if row_type == "compaction":
        return EventKind.SYSTEM_EVENT

    if row_type == "custom":
        custom_type = str(row.get("customType", "")).lower()
        if custom_type.startswith("model"):
            return EventKind.SYSTEM_EVENT

    if row_type.startswith("tool") and "result" in row_type:
        return EventKind.TOOL_RESULT
    if row_type.startswith("tool"):
        return EventKind.TOOL_CALL

    if row_type == "message":
        if role == "toolresult":
            return EventKind.TOOL_RESULT
        if role == "assistant" and tool_calls:
            return EventKind.TOOL_CALL
        if role == "assistant":
            return EventKind.AGENT_OUTPUT
        if role == "user":
            if _looks_like_system_text(text) and _looks_like_cron_text(text):
                return EventKind.CRON_FIRE
            if _looks_like_system_text(text):
                return EventKind.SYSTEM_EVENT
            return EventKind.AGENT_INPUT

    return EventKind.NOTE


def import_openclaw_session(
    session_jsonl: Path,
    out_events: Path,
    run_id: str,
    include_content: bool = False,
    start_sequence_id: int = 1,
    profile: str = "lean",
) -> int:
    writer = JsonlTraceWriter(out_events, flush_every=200)
    seq = start_sequence_id
    count = 0

    keep_content = include_content or profile in {"bridge", "debug"}

    with session_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            role, text, usage, tool_calls = _extract_openclaw_fields(row)
            usage_cost = usage.get("cost") if isinstance(usage.get("cost"), dict) else {}
            token_total = usage.get("totalTokens") if isinstance(usage.get("totalTokens"), int) else None
            cost_usd = usage_cost.get("total") if isinstance(usage_cost.get("total"), (int, float)) else None
            kind = _infer_kind(row, role=role, text=text, tool_calls=tool_calls)

            attrs: dict[str, Any] = {
                "role": role or None,
                "type": row.get("type"),
                "content_chars": len(text),
                "profile": profile,
            }
            if row.get("customType"):
                attrs["custom_type"] = row.get("customType")
            if tool_calls:
                attrs["tool_calls"] = tool_calls
                attrs["tool_call_count"] = len(tool_calls)
            if keep_content:
                attrs["content"] = text
                if profile == "debug":
                    attrs["raw"] = row

            event = TraceEvent(
                run_id=run_id,
                sequence_id=seq,
                kind=kind,
                actor="openclaw",
                attrs=attrs,
                token_estimate=token_total if token_total is not None else (max(1, len(text) // 4) if text else 0),
                prompt_chars=len(text) if role == "user" else None,
                response_chars=len(text) if role in {"assistant", "system", "toolresult"} else None,
                cost_usd_micros=int(cost_usd * 1_000_000) if cost_usd is not None else None,
            )
            writer.append(event)
            seq += 1
            count += 1

    writer.close()
    return count
