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
- Phase A.1 classification split:
  - `tool.call` (including assistant message toolCall payloads)
  - `tool.result`
  - `cron.fire`
  - `system.event`
- Import profile controls:
  - `profile=lean` (default)
  - `profile=bridge` (include content, no raw payload)
  - `profile=debug` (include content + raw row)
- Phase A.2 bridge export controls:
  - `export-agent-lightning --format messages`
  - `export-agent-lightning --format triplets`

## Non-goals
- No online RL loop
- No heavy backend requirement
- No intrusive OpenClaw core patches in v0

## Positioning
- Adjacent projects exist (memory layers, observability stacks, training frameworks), but they do not replace an OpenClaw-native runtime adapter.
- TraceBridge focuses on immediate OpenClaw operability and token-efficient capture first, then replay and optional integration bridges.
- See `docs/LANDSCAPE_AND_RATIONALE.md` for detail.

## License posture
- Agent Lightning reference repo is MIT.
- We may reuse ideas and selected implementation patterns.
- If code is copied/adapted later, preserve MIT notices and attribution.

## Acceptance criteria
- Import any OpenClaw session JSONL without crashing
- Produce valid `tracebridge.event.v1` rows
- Deterministic sequence IDs
- Summaries include event count, rough token/cost fields (if present)
- Correctly split key runtime rows into `tool.call`, `tool.result`, `cron.fire`, `system.event`
- `profile=lean` avoids raw payload bloat by default
- Bridge export writes deterministic rows for `messages` and `triplets` formats
