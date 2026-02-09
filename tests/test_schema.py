from openclaw_tracebridge.schema import EventKind, TraceEvent


def test_trace_event_defaults() -> None:
    e = TraceEvent(run_id="run_x", sequence_id=1, kind=EventKind.NOTE)
    assert e.schema_version == "tracebridge.event.v1"
    assert e.event_id.startswith("ev_")
