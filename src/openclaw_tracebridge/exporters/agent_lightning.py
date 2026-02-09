from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..io import iter_events
from ..schema import EventKind, TraceEvent


@dataclass
class ExportSummary:
    format: str
    rows_written: int
    skipped_missing_content: int
    skipped_unpaired: int


@dataclass
class _TurnPair:
    input_event: TraceEvent
    output_event: TraceEvent
    middle_events: list[TraceEvent]


def _content_of(event: TraceEvent) -> str:
    content = event.attrs.get("content")
    return str(content).strip() if isinstance(content, str) else ""


def _iter_turn_pairs(events: list[TraceEvent]) -> tuple[list[_TurnPair], int, int]:
    ordered = sorted(events, key=lambda e: e.sequence_id)

    pairs: list[_TurnPair] = []
    pending_input: TraceEvent | None = None
    middle: list[TraceEvent] = []
    skipped_missing = 0
    skipped_unpaired = 0

    for event in ordered:
        if event.kind == EventKind.AGENT_INPUT:
            if pending_input is not None:
                skipped_unpaired += 1
            pending_input = event
            middle = []
            continue

        if pending_input is None:
            continue

        middle.append(event)

        if event.kind == EventKind.AGENT_OUTPUT:
            input_text = _content_of(pending_input)
            output_text = _content_of(event)
            if not input_text or not output_text:
                skipped_missing += 1
                pending_input = None
                middle = []
                continue

            pairs.append(
                _TurnPair(
                    input_event=pending_input,
                    output_event=event,
                    middle_events=middle[:-1],  # exclude output event itself
                )
            )
            pending_input = None
            middle = []

    if pending_input is not None:
        skipped_unpaired += 1

    return pairs, skipped_missing, skipped_unpaired


def _count_middle_events(middle: list[TraceEvent]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for e in middle:
        key = str(e.kind)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _heuristic_reward(pair: _TurnPair) -> float:
    output = _content_of(pair.output_event).lower()
    counts = _count_middle_events(pair.middle_events)

    reward = 0.4
    if output:
        reward += 0.25
    if counts.get(str(EventKind.TOOL_RESULT), 0) > 0:
        reward += 0.2
    if counts.get(str(EventKind.SYSTEM_EVENT), 0) > 0:
        reward -= 0.1

    if any(word in output for word in ["error", "failed", "exception", "timeout"]):
        reward -= 0.3

    return max(0.0, min(1.0, round(reward, 4)))


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def export_to_agent_lightning_messages(events_path: Path, out_path: Path) -> ExportSummary:
    events = list(iter_events(events_path))
    pairs, skipped_missing, skipped_unpaired = _iter_turn_pairs(events)

    rows: list[dict[str, Any]] = []
    for idx, pair in enumerate(pairs, start=1):
        counts = _count_middle_events(pair.middle_events)
        rows.append(
            {
                "schema": "tracebridge.agent_lightning.messages.v0",
                "id": f"msgpair_{idx:06d}",
                "run_id": pair.input_event.run_id,
                "messages": [
                    {"role": "user", "content": _content_of(pair.input_event)},
                    {"role": "assistant", "content": _content_of(pair.output_event)},
                ],
                "metadata": {
                    "input_event_id": pair.input_event.event_id,
                    "output_event_id": pair.output_event.event_id,
                    "input_sequence_id": pair.input_event.sequence_id,
                    "output_sequence_id": pair.output_event.sequence_id,
                    "middle_counts": counts,
                    "input_token_estimate": pair.input_event.token_estimate,
                    "output_token_estimate": pair.output_event.token_estimate,
                    "cost_usd_micros": (pair.input_event.cost_usd_micros or 0)
                    + (pair.output_event.cost_usd_micros or 0),
                },
            }
        )

    _write_jsonl(out_path, rows)
    return ExportSummary(
        format="messages",
        rows_written=len(rows),
        skipped_missing_content=skipped_missing,
        skipped_unpaired=skipped_unpaired,
    )


def export_to_agent_lightning_triplets(
    events_path: Path,
    out_path: Path,
    reward_mode: str = "none",
) -> ExportSummary:
    events = list(iter_events(events_path))
    pairs, skipped_missing, skipped_unpaired = _iter_turn_pairs(events)

    rows: list[dict[str, Any]] = []
    for idx, pair in enumerate(pairs, start=1):
        counts = _count_middle_events(pair.middle_events)

        reward: float | None
        if reward_mode == "heuristic-basic":
            reward = _heuristic_reward(pair)
        else:
            reward = None

        rows.append(
            {
                "schema": "tracebridge.agent_lightning.triplet.v0",
                "id": f"triplet_{idx:06d}",
                "run_id": pair.input_event.run_id,
                "state_text": _content_of(pair.input_event),
                "action_text": _content_of(pair.output_event),
                "reward": reward,
                "metadata": {
                    "input_event_id": pair.input_event.event_id,
                    "output_event_id": pair.output_event.event_id,
                    "input_sequence_id": pair.input_event.sequence_id,
                    "output_sequence_id": pair.output_event.sequence_id,
                    "middle_counts": counts,
                    "reward_mode": reward_mode,
                },
            }
        )

    _write_jsonl(out_path, rows)
    return ExportSummary(
        format="triplets",
        rows_written=len(rows),
        skipped_missing_content=skipped_missing,
        skipped_unpaired=skipped_unpaired,
    )
