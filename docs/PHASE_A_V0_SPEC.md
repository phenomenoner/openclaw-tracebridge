# Phase A v0 Spec (Adapter MVP)

## Goal
Start collecting useful traces immediately with minimal runtime risk.

## Scope
- Stable `tracebridge.event.v1` JSONL schema
- CLI tools for:
  - run init
  - OpenClaw session JSONL import
  - basic stats summary
- Lean-by-default payload (store lengths/metadata, not full content)

## Non-goals
- No online RL loop
- No heavy backend requirement
- No intrusive OpenClaw core patches in v0

## License posture
- Agent Lightning reference repo is MIT.
- We may reuse ideas and selected implementation patterns.
- If code is copied/adapted later, preserve MIT notices and attribution.

## Acceptance criteria
- Import any OpenClaw session JSONL without crashing
- Produce valid `tracebridge.event.v1` rows
- Deterministic sequence IDs
- Summaries include event count, rough token/cost fields (if present)
