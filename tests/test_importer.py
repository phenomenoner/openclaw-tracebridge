import json
from pathlib import Path

from openclaw_tracebridge.adapters.openclaw_session import import_openclaw_session
from openclaw_tracebridge.io import iter_events


def test_import_openclaw_session(tmp_path: Path) -> None:
    src = tmp_path / "session.jsonl"
    out = tmp_path / "events.jsonl"

    rows = [
        {
            "type": "message",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "hello"}],
                "usage": {"totalTokens": 11, "cost": {"total": 0.0001}},
            },
        },
        {
            "type": "message",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "hi there"}],
                "usage": {"totalTokens": 13, "cost": {"total": 0.0002}},
            },
        },
        {"type": "tool.call", "content": {"name": "read"}},
    ]
    src.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    n = import_openclaw_session(src, out, run_id="run_demo")
    events = list(iter_events(out))

    assert n == 3
    assert len(events) == 3
    assert events[0].sequence_id == 1
    assert events[-1].sequence_id == 3
    assert str(events[0].kind) == "agent.input"
    assert str(events[1].kind) == "agent.output"
    assert events[0].token_estimate == 11
    assert events[1].cost_usd_micros == 200
