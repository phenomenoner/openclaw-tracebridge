import json
from pathlib import Path

from openclaw_tracebridge.cli import main


def _write_events(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def test_export_agent_lightning_messages(tmp_path: Path) -> None:
    events = tmp_path / "events.jsonl"
    out = tmp_path / "messages.jsonl"

    rows = [
        {
            "schema_version": "tracebridge.event.v1",
            "event_id": "ev_1",
            "run_id": "run_demo",
            "sequence_id": 1,
            "ts": "2026-02-09T00:00:00Z",
            "kind": "agent.input",
            "actor": "openclaw",
            "attrs": {"content": "hello"},
            "token_estimate": 3,
        },
        {
            "schema_version": "tracebridge.event.v1",
            "event_id": "ev_2",
            "run_id": "run_demo",
            "sequence_id": 2,
            "ts": "2026-02-09T00:00:01Z",
            "kind": "tool.call",
            "actor": "openclaw",
            "attrs": {"content": "calling read"},
        },
        {
            "schema_version": "tracebridge.event.v1",
            "event_id": "ev_3",
            "run_id": "run_demo",
            "sequence_id": 3,
            "ts": "2026-02-09T00:00:02Z",
            "kind": "agent.output",
            "actor": "openclaw",
            "attrs": {"content": "hi"},
            "token_estimate": 2,
        },
    ]
    _write_events(events, rows)

    rc = main(
        [
            "export-agent-lightning",
            "--events",
            str(events),
            "--out",
            str(out),
            "--format",
            "messages",
        ]
    )
    assert rc == 0

    lines = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    assert lines[0]["schema"] == "tracebridge.agent_lightning.messages.v0"
    assert lines[0]["messages"][0]["content"] == "hello"
    assert lines[0]["messages"][1]["content"] == "hi"


def test_export_agent_lightning_triplets_heuristic_reward(tmp_path: Path) -> None:
    events = tmp_path / "events.jsonl"
    out = tmp_path / "triplets.jsonl"

    rows = [
        {
            "schema_version": "tracebridge.event.v1",
            "event_id": "ev_10",
            "run_id": "run_demo",
            "sequence_id": 10,
            "ts": "2026-02-09T00:00:10Z",
            "kind": "agent.input",
            "actor": "openclaw",
            "attrs": {"content": "search docs"},
        },
        {
            "schema_version": "tracebridge.event.v1",
            "event_id": "ev_11",
            "run_id": "run_demo",
            "sequence_id": 11,
            "ts": "2026-02-09T00:00:11Z",
            "kind": "tool.result",
            "actor": "openclaw",
            "attrs": {"content": "docs found"},
        },
        {
            "schema_version": "tracebridge.event.v1",
            "event_id": "ev_12",
            "run_id": "run_demo",
            "sequence_id": 12,
            "ts": "2026-02-09T00:00:12Z",
            "kind": "agent.output",
            "actor": "openclaw",
            "attrs": {"content": "here are the docs"},
        },
    ]
    _write_events(events, rows)

    rc = main(
        [
            "export-agent-lightning",
            "--events",
            str(events),
            "--out",
            str(out),
            "--format",
            "triplets",
            "--reward-mode",
            "heuristic-basic",
        ]
    )
    assert rc == 0

    lines = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    assert lines[0]["schema"] == "tracebridge.agent_lightning.triplet.v0"
    assert isinstance(lines[0]["reward"], float)
    assert 0.0 <= lines[0]["reward"] <= 1.0
