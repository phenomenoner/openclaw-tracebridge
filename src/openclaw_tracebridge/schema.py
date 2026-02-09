from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class EventKind(StrEnum):
    AGENT_INPUT = "agent.input"
    AGENT_OUTPUT = "agent.output"
    TOOL_CALL = "tool.call"
    TOOL_RESULT = "tool.result"
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"
    CRON_FIRE = "cron.fire"
    HEARTBEAT = "heartbeat"
    NOTE = "note"


class TraceEvent(BaseModel):
    schema_version: Literal["tracebridge.event.v1"] = "tracebridge.event.v1"
    event_id: str = Field(default_factory=lambda: f"ev_{uuid4().hex}")
    run_id: str
    sequence_id: int = Field(ge=1)
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    kind: EventKind
    actor: str = "openclaw"
    attrs: dict[str, Any] = Field(default_factory=dict)

    token_estimate: int | None = Field(default=None, ge=0)
    prompt_chars: int | None = Field(default=None, ge=0)
    response_chars: int | None = Field(default=None, ge=0)
    cost_usd_micros: int | None = Field(default=None, ge=0)


class RunMeta(BaseModel):
    schema_version: Literal["tracebridge.run.v1"] = "tracebridge.run.v1"
    run_id: str
    session_key: str | None = None
    source: str = "openclaw"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def new_run_id(prefix: str = "run") -> str:
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}"
