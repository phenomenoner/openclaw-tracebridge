from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .schema import TraceEvent


class JsonlTraceWriter:
    def __init__(self, path: Path, flush_every: int = 1) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.flush_every = max(1, flush_every)
        self._buffer: list[str] = []

    def append(self, event: TraceEvent) -> None:
        self._buffer.append(event.model_dump_json())
        if len(self._buffer) >= self.flush_every:
            self.flush()

    def flush(self) -> None:
        if not self._buffer:
            return
        with self.path.open("a", encoding="utf-8") as f:
            f.write("\n".join(self._buffer) + "\n")
        self._buffer.clear()

    def close(self) -> None:
        self.flush()


def iter_events(path: Path) -> Iterable[TraceEvent]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield TraceEvent.model_validate(json.loads(line))
