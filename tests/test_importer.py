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


def test_import_openclaw_session_phase_a1_kind_split(tmp_path: Path) -> None:
    src = tmp_path / "session_a1.jsonl"
    out = tmp_path / "events_a1.jsonl"

    rows = [
        {
            "type": "message",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "will call tool"},
                    {"type": "toolCall", "id": "c1", "name": "web_fetch", "arguments": {"url": "x"}},
                ],
            },
        },
        {
            "type": "message",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "System: [2026-01-01 00:00:00 UTC] Cron: HEARTBEAT_OK"}],
            },
        },
        {
            "type": "message",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "System: [2026-01-01 00:00:00 UTC] Cron: Usage report"}],
            },
        },
        {
            "type": "custom",
            "customType": "model-snapshot",
            "data": {"modelId": "gpt-x"},
        },
    ]
    src.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    n = import_openclaw_session(src, out, run_id="run_phase_a1")
    events = list(iter_events(out))

    assert n == 4
    assert str(events[0].kind) == "tool.call"
    assert events[0].attrs["tool_calls"] == ["web_fetch"]
    assert str(events[1].kind) == "heartbeat"
    assert str(events[2].kind) == "cron.fire"
    assert str(events[3].kind) == "system.event"


def test_import_openclaw_session_bridge_profile_includes_content_only(tmp_path: Path) -> None:
    src = tmp_path / "session_bridge.jsonl"
    out = tmp_path / "events_bridge.jsonl"

    row = {
        "type": "message",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": "hello bridge"}],
        },
    }
    src.write_text(json.dumps(row) + "\n", encoding="utf-8")

    import_openclaw_session(src, out, run_id="run_bridge", profile="bridge")
    events = list(iter_events(out))

    assert len(events) == 1
    assert events[0].attrs.get("profile") == "bridge"
    assert events[0].attrs.get("content") == "hello bridge"
    assert "raw" not in events[0].attrs


def test_import_openclaw_session_debug_profile_includes_raw(tmp_path: Path) -> None:
    src = tmp_path / "session_debug.jsonl"
    out = tmp_path / "events_debug.jsonl"

    row = {
        "type": "message",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": "hello debug"}],
        },
    }
    src.write_text(json.dumps(row) + "\n", encoding="utf-8")

    import_openclaw_session(src, out, run_id="run_debug", profile="debug")
    events = list(iter_events(out))

    assert len(events) == 1
    assert events[0].attrs.get("profile") == "debug"
    assert "content" in events[0].attrs
    assert "raw" in events[0].attrs
