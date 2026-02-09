from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RuntimeSmokeSummary:
    installed: bool
    ok: bool
    reason: str | None
    rows_total: int
    rows_used: int
    spans_written: int
    rollout_id: str | None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _valid_messages_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if row.get("schema") != "tracebridge.agent_lightning.messages.v0":
            continue
        msgs = row.get("messages")
        if not isinstance(msgs, list) or len(msgs) < 2:
            continue
        u = msgs[0].get("content") if isinstance(msgs[0], dict) else None
        a = msgs[1].get("content") if isinstance(msgs[1], dict) else None
        if not isinstance(u, str) or not u.strip():
            continue
        if not isinstance(a, str) or not a.strip():
            continue
        out.append(row)
    return out


def _reward_from_assistant_text(text: str) -> float:
    low = text.lower()
    reward = 0.5
    if len(text.strip()) > 0:
        reward += 0.2
    if any(k in low for k in ["error", "failed", "exception", "timeout"]):
        reward -= 0.3
    return max(0.0, min(1.0, round(reward, 4)))


def run_agent_lightning_runtime_smoke(messages_path: Path, *, max_rows: int = 10) -> RuntimeSmokeSummary:
    try:
        from agentlightning import OtelTracer, emit_reward
        from agentlightning.store import InMemoryLightningStore
    except Exception:
        return RuntimeSmokeSummary(
            installed=False,
            ok=False,
            reason="agentlightning not installed (run with: uv run --with agentlightning ...)",
            rows_total=0,
            rows_used=0,
            spans_written=0,
            rollout_id=None,
        )

    rows_all = _read_jsonl(messages_path)
    rows_ok = _valid_messages_rows(rows_all)
    rows_used = rows_ok[:max_rows]

    if not rows_used:
        return RuntimeSmokeSummary(
            installed=True,
            ok=False,
            reason="no valid message rows",
            rows_total=len(rows_all),
            rows_used=0,
            spans_written=0,
            rollout_id=None,
        )

    async def _run() -> tuple[int, str]:
        tracer = OtelTracer()
        store = InMemoryLightningStore()
        rollout = await store.start_rollout(input={"origin": "tracebridge.runtime_smoke"})

        with tracer.lifespan(store):
            for i, row in enumerate(rows_used, start=1):
                messages = row["messages"]
                user_text = str(messages[0].get("content", ""))
                assistant_text = str(messages[1].get("content", ""))
                reward = _reward_from_assistant_text(assistant_text)

                async with tracer.trace_context(
                    f"tb-runtime-{i}",
                    store=store,
                    rollout_id=rollout.rollout_id,
                    attempt_id=rollout.attempt.attempt_id,
                ) as t:
                    with t.start_as_current_span("tracebridge.user"):
                        _ = len(user_text)
                    with t.start_as_current_span("tracebridge.assistant"):
                        _ = len(assistant_text)
                    emit_reward(reward)

        spans = await store.query_spans(rollout_id=rollout.rollout_id)
        return len(spans), rollout.rollout_id

    spans_written, rollout_id = asyncio.run(_run())
    ok = spans_written > 0
    return RuntimeSmokeSummary(
        installed=True,
        ok=ok,
        reason=None if ok else "no spans written",
        rows_total=len(rows_all),
        rows_used=len(rows_used),
        spans_written=spans_written,
        rollout_id=rollout_id,
    )
